import aiofiles
from pathlib import Path
from app.core.config import settings
from app.providers.storage.base import BaseStorageProvider


class LocalStorageProvider(BaseStorageProvider):
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(self, relative_path: str, content: bytes) -> str:
        full_path = self.base_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)
        return str(full_path)

    async def read_file(self, storage_path: str) -> bytes:
        path = Path(storage_path)
        if not path.is_absolute():
            path = self.base_path / storage_path
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    async def delete_file(self, storage_path: str) -> bool:
        path = Path(storage_path)
        if not path.is_absolute():
            path = self.base_path / storage_path
        if path.exists():
            path.unlink()
            return True
        return False
