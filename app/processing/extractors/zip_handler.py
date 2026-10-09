import io
import os
import zipfile
from typing import List, Tuple
from app.core.config import settings
from app.core.exceptions import FileValidationError


class SafeZipHandler:
    def __init__(
        self,
        max_zip_size_mb: int = settings.MAX_UPLOAD_SIZE_MB,
        max_extracted_size_mb: int = settings.MAX_ZIP_EXTRACTED_SIZE_MB,
        max_file_count: int = settings.MAX_ZIP_FILES,
        max_nesting_depth: int = settings.MAX_ZIP_NESTING_DEPTH,
    ):
        self.max_zip_bytes = max_zip_size_mb * 1024 * 1024
        self.max_extracted_bytes = max_extracted_size_mb * 1024 * 1024
        self.max_file_count = max_file_count
        self.max_nesting_depth = max_nesting_depth

    def extract_files(self, zip_bytes: bytes) -> List[Tuple[str, bytes]]:
        if len(zip_bytes) > self.max_zip_bytes:
            raise FileValidationError(f"ZIP file size exceeds limit of {self.max_zip_bytes / (1024*1024)}MB")

        extracted_files: List[Tuple[str, bytes]] = []
        total_extracted_size = 0

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            infolist = zf.infolist()
            if len(infolist) > self.max_file_count:
                raise FileValidationError(
                    f"ZIP archive contains {len(infolist)} files, exceeding limit of {self.max_file_count}"
                )

            for member in infolist:
                if member.is_dir():
                    continue

                # Zip Slip / Path Traversal Prevention
                norm_path = os.path.normpath(member.filename)
                if norm_path.startswith("..") or os.path.isabs(norm_path):
                    raise FileValidationError(f"Unsafe ZIP path traversal detected: {member.filename}")

                # Nesting depth check
                depth = len(norm_path.split(os.sep)) - 1
                if depth > self.max_nesting_depth:
                    continue  # Skip deeply nested files

                # Check extracted size
                total_extracted_size += member.file_size
                if total_extracted_size > self.max_extracted_bytes:
                    raise FileValidationError(
                        f"ZIP extracted size exceeds limit of {self.max_extracted_bytes / (1024*1024)}MB"
                    )

                file_data = zf.read(member.filename)
                filename = os.path.basename(member.filename)
                if filename:
                    extracted_files.append((filename, file_data))

        return extracted_files
