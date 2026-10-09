from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from local LLM given chat messages."""
        pass
