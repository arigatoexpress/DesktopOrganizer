"""File scanner for discovering and extracting file metadata."""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Iterator
from datetime import datetime
import os

from config import Config, DEFAULT_CONFIG


@dataclass
class FileInfo:
    """Information about a scanned file."""
    path: Path
    name: str
    extension: str
    size_bytes: int
    modified_time: datetime
    created_time: datetime
    content: Optional[str] = None
    mime_type: Optional[str] = None

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)

    @property
    def is_text_file(self) -> bool:
        return self.extension.lower() in DEFAULT_CONFIG.text_extensions

    def __repr__(self) -> str:
        return f"FileInfo({self.name}, {self.size_mb:.2f}MB)"


class FileScanner:
    """Scans directories and extracts file information."""

    def __init__(self, config: Config = None):
        self.config = config or DEFAULT_CONFIG
        self._magic = None

    def _get_magic(self):
        """Lazy load python-magic."""
        if self._magic is None:
            try:
                import magic
                self._magic = magic.Magic(mime=True)
            except ImportError:
                self._magic = False  # Mark as unavailable
        return self._magic if self._magic else None

    def scan_directory(self, directory: Path, recursive: bool = True) -> Iterator[FileInfo]:
        """
        Scan a directory and yield FileInfo objects for each file.

        Args:
            directory: Path to scan
            recursive: Whether to scan subdirectories

        Yields:
            FileInfo objects for each file found
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        pattern = "**/*" if recursive else "*"

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                # Skip hidden files
                if file_path.name.startswith('.'):
                    continue

                # Skip files in hidden directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue

                file_info = self._get_file_info(file_path)
                if file_info:
                    yield file_info

    def _get_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """Extract information from a single file."""
        try:
            stat = file_path.stat()
            extension = file_path.suffix.lower()

            # Skip files that are too large
            size_mb = stat.st_size / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                return None

            # Skip certain extensions
            if extension in self.config.skip_extensions:
                return None

            # Get MIME type if available
            mime_type = None
            magic_instance = self._get_magic()
            if magic_instance:
                try:
                    mime_type = magic_instance.from_file(str(file_path))
                except Exception:
                    pass

            # Extract content for text files
            content = None
            if extension in self.config.text_extensions:
                content = self._read_text_content(file_path)
            elif extension == '.pdf':
                content = self._read_pdf_content(file_path)

            return FileInfo(
                path=file_path,
                name=file_path.name,
                extension=extension,
                size_bytes=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                created_time=datetime.fromtimestamp(stat.st_ctime),
                content=content,
                mime_type=mime_type
            )
        except (PermissionError, OSError) as e:
            return None

    def _read_text_content(self, file_path: Path) -> Optional[str]:
        """Read text content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(self.config.max_content_chars)
                return content.strip() if content else None
        except Exception:
            return None

    def _read_pdf_content(self, file_path: Path) -> Optional[str]:
        """Extract text content from a PDF file."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(file_path))
            text_parts = []
            total_chars = 0

            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                total_chars += len(page_text)
                if total_chars >= self.config.max_content_chars:
                    break

            content = "\n".join(text_parts)[:self.config.max_content_chars]
            return content.strip() if content else None
        except ImportError:
            return None
        except Exception:
            return None

    def get_file_count(self, directory: Path, recursive: bool = True) -> int:
        """Get the count of files in a directory."""
        count = 0
        for _ in self.scan_directory(directory, recursive):
            count += 1
        return count


def scan_files(directory: Path, config: Config = None) -> list[FileInfo]:
    """Convenience function to scan all files in a directory."""
    scanner = FileScanner(config)
    return list(scanner.scan_directory(directory))
