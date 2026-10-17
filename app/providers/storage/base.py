from abc import ABC, abstractmethod


class BaseStorageProvider(ABC):
    @abstractmethod
    async def save_file(self, relative_path: str, content: bytes) -> str:
        """Save file content and return storage path."""
        pass

    @abstractmethod
    async def read_file(self, storage_path: str) -> bytes:
        """Read and return file content bytes."""
        pass

    @abstractmethod
    async def delete_file(self, storage_path: str) -> bool:
        """Delete file at storage path."""
        pass
