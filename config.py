"""Configuration management for the AI File Organizer."""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class Config:
    """Configuration settings for the file organizer."""

    # Ollama settings
    ollama_model: str = "llama3.2"
    ollama_host: str = "http://localhost:11434"

    # Processing settings
    max_file_size_mb: int = 50  # Skip files larger than this
    max_content_chars: int = 4000  # Max chars to send to LLM
    batch_size: int = 10  # Files to process in batch

    # File types to read content from
    text_extensions: set = field(default_factory=lambda: {
        '.txt', '.md', '.rst', '.json', '.yaml', '.yml', '.xml', '.csv',
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
        '.go', '.rs', '.rb', '.php', '.html', '.css', '.scss', '.sql',
        '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd',
        '.ini', '.cfg', '.conf', '.toml', '.env', '.gitignore',
        '.dockerfile', '.makefile'
    })

    # File types to skip entirely
    skip_extensions: set = field(default_factory=lambda: {
        '.exe', '.dll', '.so', '.dylib', '.bin',
        '.iso', '.dmg', '.img',
        '.lock', '.log'
    })

    # Output settings
    output_dir_name: str = "Organized"
    undo_log_file: str = "undo_log.json"

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            'ollama_model': self.ollama_model,
            'ollama_host': self.ollama_host,
            'max_file_size_mb': self.max_file_size_mb,
            'max_content_chars': self.max_content_chars,
            'batch_size': self.batch_size,
            'text_extensions': list(self.text_extensions),
            'skip_extensions': list(self.skip_extensions),
            'output_dir_name': self.output_dir_name,
            'undo_log_file': self.undo_log_file
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        """Create config from dictionary."""
        if 'text_extensions' in data:
            data['text_extensions'] = set(data['text_extensions'])
        if 'skip_extensions' in data:
            data['skip_extensions'] = set(data['skip_extensions'])
        return cls(**data)

    def save(self, path: Path) -> None:
        """Save config to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> 'Config':
        """Load config from JSON file."""
        if not path.exists():
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))


# Global default config
DEFAULT_CONFIG = Config()
