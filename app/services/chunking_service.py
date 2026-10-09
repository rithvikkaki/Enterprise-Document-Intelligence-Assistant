import os
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger

_hf_tokenizer = None


def get_tokenizer():
    global _hf_tokenizer
    if os.environ.get("TESTING") == "true" or settings.ENVIRONMENT == "testing":
        return None

    if _hf_tokenizer is None:
        try:
            from transformers import AutoTokenizer
            _hf_tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL)
        except Exception:
            _hf_tokenizer = None
    return _hf_tokenizer


def count_tokens(text: str) -> int:
    tokenizer = get_tokenizer()
    if tokenizer:
        try:
            return len(tokenizer.encode(text, add_special_tokens=False))
        except Exception:
            pass
    # Fallback word count multiplier (~1.3 tokens/word)
    words = text.split()
    return int(len(words) * 1.3) or len(words)


class ChunkData(BaseModel):
    chunk_index: int
    content: str
    token_count: int
    metadata: Dict[str, Any] = {}


class BaseChunker(ABC):
    @abstractmethod
    def create_chunks(self, text: str, initial_metadata: Optional[Dict[str, Any]] = None) -> List[ChunkData]:
        pass


class FixedSizeChunker(BaseChunker):
    def __init__(self, max_tokens: int = settings.DEFAULT_CHUNK_SIZE, overlap: int = settings.DEFAULT_CHUNK_OVERLAP):
        self.max_tokens = max_tokens
        self.overlap = overlap

    def create_chunks(self, text: str, initial_metadata: Optional[Dict[str, Any]] = None) -> List[ChunkData]:
        if not text.strip():
            return []

        words = text.split()
        chunks: List[ChunkData] = []
        chunk_idx = 0
        i = 0

        while i < len(words):
            chunk_words = []
            curr_tokens = 0
            j = i
            while j < len(words) and curr_tokens < self.max_tokens:
                chunk_words.append(words[j])
                curr_tokens = count_tokens(" ".join(chunk_words))
                j += 1

            chunk_text = " ".join(chunk_words)
            meta = dict(initial_metadata or {})
            meta["strategy"] = "fixed_size"

            chunks.append(
                ChunkData(
                    chunk_index=chunk_idx,
                    content=chunk_text,
                    token_count=curr_tokens,
                    metadata=meta,
                )
            )
            chunk_idx += 1

            step = max(1, len(chunk_words) - max(1, self.overlap // 2))
            i += step

        return chunks


class SentenceBoundaryChunker(BaseChunker):
    def __init__(self, max_tokens: int = settings.DEFAULT_CHUNK_SIZE, overlap: int = settings.DEFAULT_CHUNK_OVERLAP):
        self.max_tokens = max_tokens
        self.overlap = overlap

    def create_chunks(self, text: str, initial_metadata: Optional[Dict[str, Any]] = None) -> List[ChunkData]:
        if not text.strip():
            return []

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: List[ChunkData] = []
        chunk_idx = 0
        current_sentences: List[str] = []
        current_token_count = 0

        for sent in sentences:
            sent_tokens = count_tokens(sent)
            if current_token_count + sent_tokens > self.max_tokens and current_sentences:
                chunk_text = " ".join(current_sentences)
                meta = dict(initial_metadata or {})
                meta["strategy"] = "sentence_boundary"
                chunks.append(
                    ChunkData(
                        chunk_index=chunk_idx,
                        content=chunk_text,
                        token_count=current_token_count,
                        metadata=meta,
                    )
                )
                chunk_idx += 1

                current_sentences = current_sentences[-2:] if len(current_sentences) >= 2 else []
                current_token_count = sum(count_tokens(s) for s in current_sentences)

            current_sentences.append(sent)
            current_token_count += sent_tokens

        if current_sentences:
            chunk_text = " ".join(current_sentences)
            meta = dict(initial_metadata or {})
            meta["strategy"] = "sentence_boundary"
            chunks.append(
                ChunkData(
                    chunk_index=chunk_idx,
                    content=chunk_text,
                    token_count=current_token_count,
                    metadata=meta,
                )
            )

        return chunks


class MarkdownChunker(BaseChunker):
    def __init__(self, max_tokens: int = settings.DEFAULT_CHUNK_SIZE):
        self.max_tokens = max_tokens
        self.fallback = SentenceBoundaryChunker(max_tokens=max_tokens)

    def create_chunks(self, text: str, initial_metadata: Optional[Dict[str, Any]] = None) -> List[ChunkData]:
        sections = re.split(r"\n(?=#+\s)", text)
        if len(sections) <= 1:
            return self.fallback.create_chunks(text, initial_metadata)

        chunks: List[ChunkData] = []
        chunk_idx = 0
        for sec in sections:
            sec_chunks = self.fallback.create_chunks(sec, initial_metadata)
            for c in sec_chunks:
                c.chunk_index = chunk_idx
                c.metadata["strategy"] = "markdown_heading"
                chunks.append(c)
                chunk_idx += 1

        return chunks
