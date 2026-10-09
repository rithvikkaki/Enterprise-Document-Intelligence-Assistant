import pytest
from app.services.chunking_service import FixedSizeChunker, SentenceBoundaryChunker, MarkdownChunker


@pytest.mark.unit
def test_fixed_size_chunker():
    text = "Sentence one. " * 100
    chunker = FixedSizeChunker(max_tokens=50, overlap=10)
    chunks = chunker.create_chunks(text)
    assert len(chunks) > 1
    for c in chunks:
        assert c.token_count <= 65
        assert c.content


@pytest.mark.unit
def test_sentence_boundary_chunker():
    text = "The quick brown fox jumps over the lazy dog. " * 20
    chunker = SentenceBoundaryChunker(max_tokens=50)
    chunks = chunker.create_chunks(text)
    assert len(chunks) > 0
    for c in chunks:
        assert len(c.content) > 0


@pytest.mark.unit
def test_markdown_chunker():
    md_text = "# Header 1\nSection 1 text.\n\n## Header 2\nSection 2 text."
    chunker = MarkdownChunker(max_tokens=100)
    chunks = chunker.create_chunks(md_text)
    assert len(chunks) >= 2
