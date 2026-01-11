"""File mover with undo support and dry-run capability."""

from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
import json
import shutil

from analyzer import AnalysisResult
from config import Config, DEFAULT_CONFIG


@dataclass
class MoveOperation:
    """Represents a single file move operation."""
    source: str
    destination: str
    category: str
    reasoning: str
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'MoveOperation':
        return cls(**data)


@dataclass
class OrganizationSession:
    """A session of file organization operations."""
    session_id: str
    timestamp: str
    source_directory: str
    output_directory: str
    operations: list[MoveOperation]
    completed: bool = False

    def to_dict(self) -> dict:
        return {
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'source_directory': self.source_directory,
            'output_directory': self.output_directory,
            'operations': [op.to_dict() for op in self.operations],
            'completed': self.completed
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'OrganizationSession':
        operations = [MoveOperation.from_dict(op) for op in data.get('operations', [])]
        return cls(
            session_id=data['session_id'],
            timestamp=data['timestamp'],
            source_directory=data['source_directory'],
            output_directory=data['output_directory'],
            operations=operations,
            completed=data.get('completed', False)
        )


class UndoLog:
    """Manages the undo log for reversing organization operations."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._sessions: list[OrganizationSession] = []
        self._load()

    def _load(self):
        """Load existing sessions from the log file."""
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r') as f:
                    data = json.load(f)
                    self._sessions = [OrganizationSession.from_dict(s) for s in data.get('sessions', [])]
            except (json.JSONDecodeError, KeyError):
                self._sessions = []

    def _save(self):
        """Save sessions to the log file."""
        # Ensure parent directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'sessions': [s.to_dict() for s in self._sessions]
        }
        with open(self.log_path, 'w') as f:
            json.dump(data, f, indent=2)

    def create_session(self, source_dir: str, output_dir: str) -> OrganizationSession:
        """Create a new organization session."""
        session = OrganizationSession(
            session_id=datetime.now().strftime('%Y%m%d_%H%M%S'),
            timestamp=datetime.now().isoformat(),
            source_directory=source_dir,
            output_directory=output_dir,
            operations=[],
            completed=False
        )
        self._sessions.append(session)
        self._save()
        return session

    def add_operation(self, session: OrganizationSession, operation: MoveOperation):
        """Add an operation to a session."""
        session.operations.append(operation)
        self._save()

    def complete_session(self, session: OrganizationSession):
        """Mark a session as complete."""
        session.completed = True
        self._save()

    def get_last_session(self) -> Optional[OrganizationSession]:
        """Get the most recent completed session."""
        for session in reversed(self._sessions):
            if session.completed:
                return session
        return None

    def remove_session(self, session: OrganizationSession):
        """Remove a session from the log."""
        self._sessions = [s for s in self._sessions if s.session_id != session.session_id]
        self._save()


class FileMover:
    """Handles file movement operations with undo support."""

    def __init__(self, output_dir: Path, config: Config = None, dry_run: bool = False):
        self.output_dir = Path(output_dir)
        self.config = config or DEFAULT_CONFIG
        self.dry_run = dry_run
        self.undo_log = UndoLog(self.output_dir / self.config.undo_log_file)
        self._current_session: Optional[OrganizationSession] = None

    def start_session(self, source_dir: Path):
        """Start a new organization session."""
        if not self.dry_run:
            self._current_session = self.undo_log.create_session(
                str(source_dir),
                str(self.output_dir)
            )

    def end_session(self):
        """End the current organization session."""
        if self._current_session and not self.dry_run:
            self.undo_log.complete_session(self._current_session)

    def move_file(self, result: AnalysisResult) -> Optional[MoveOperation]:
        """
        Move a file to its categorized location.

        Returns:
            MoveOperation describing the move, or None if failed
        """
        source = result.file_info.path
        category_path = result.category.path
        dest_dir = self.output_dir / category_path
        dest_file = dest_dir / source.name

        # Handle filename collisions
        dest_file = self._get_unique_path(dest_file)

        operation = MoveOperation(
            source=str(source),
            destination=str(dest_file),
            category=result.category.name,
            reasoning=result.reasoning,
            timestamp=datetime.now().isoformat()
        )

        if not self.dry_run:
            try:
                # Create destination directory
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Move the file
                shutil.move(str(source), str(dest_file))

                # Log the operation
                if self._current_session:
                    self.undo_log.add_operation(self._current_session, operation)
            except PermissionError:
                return None  # Skip files we can't move
            except OSError:
                return None  # Skip other OS errors

        return operation

    def _get_unique_path(self, path: Path) -> Path:
        """Get a unique file path, handling collisions."""
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def undo_last_session(self) -> tuple[bool, str, list[tuple[str, str]]]:
        """
        Undo the most recent organization session.

        Returns:
            Tuple of (success, message, list of (dest, source) moves)
        """
        session = self.undo_log.get_last_session()
        if not session:
            return False, "No sessions to undo", []

        moves = []
        errors = []

        for operation in reversed(session.operations):
            source = Path(operation.source)
            dest = Path(operation.destination)

            if dest.exists():
                try:
                    # Ensure source parent directory exists
                    source.parent.mkdir(parents=True, exist_ok=True)

                    # Move file back
                    shutil.move(str(dest), str(source))
                    moves.append((str(dest), str(source)))
                except Exception as e:
                    errors.append(f"Failed to restore {dest.name}: {e}")
            else:
                errors.append(f"File not found: {dest}")

        # Clean up empty directories in output
        self._cleanup_empty_dirs(Path(session.output_directory))

        # Remove the session from the log
        self.undo_log.remove_session(session)

        if errors:
            return False, f"Undo completed with {len(errors)} errors", moves
        return True, f"Successfully undid {len(moves)} file moves", moves

    def _cleanup_empty_dirs(self, directory: Path):
        """Remove empty directories recursively."""
        if not directory.exists():
            return

        for child in directory.iterdir():
            if child.is_dir():
                self._cleanup_empty_dirs(child)

        # Check if directory is empty now
        try:
            if directory.exists() and not any(directory.iterdir()):
                # Don't delete the root output directory
                if directory != self.output_dir:
                    directory.rmdir()
        except OSError:
            pass

    def organize_files(self, results: list[AnalysisResult], progress_callback=None) -> list[MoveOperation]:
        """
        Organize all analyzed files.

        Args:
            results: List of analysis results
            progress_callback: Optional callback(current, total, filename)

        Returns:
            List of move operations performed
        """
        operations = []
        total = len(results)

        for i, result in enumerate(results):
            operation = self.move_file(result)
            operations.append(operation)

            if progress_callback:
                progress_callback(i + 1, total, result.file_info.name)

        return operations
