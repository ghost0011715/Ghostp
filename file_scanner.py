"""File-system scanning and duplicate detection for the command-line app."""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable


class FileScanner:
    """Collect metadata about files below a directory without modifying them."""

    def __init__(self, root_path: str) -> None:
        self.root = Path(root_path).expanduser()

    def scan_directory(self, include_hidden: bool = False) -> list[dict[str, Any]]:
        """Return metadata for readable files in the selected directory tree."""
        if not self.root.exists():
            raise FileNotFoundError(f"Directory does not exist: {self.root}")
        if not self.root.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.root}")

        files: list[dict[str, Any]] = []
        for path in self.root.rglob("*"):
            if not path.is_file() or (not include_hidden and self._is_hidden(path)):
                continue
            try:
                stat = path.stat()
            except OSError:
                # A file can disappear or become inaccessible while scanning.
                continue
            files.append(
                {
                    "name": path.name,
                    "path": str(path.resolve()),
                    "relative_path": str(path.relative_to(self.root)),
                    "extension": path.suffix.lower() or "[no extension]",
                    "size_bytes": stat.st_size,
                }
            )
        return sorted(files, key=lambda item: item["path"].casefold())

    def filter_by_extension(
        self, files: Iterable[dict[str, Any]], extensions: Iterable[str]
    ) -> list[dict[str, Any]]:
        """Keep files whose extension matches one of *extensions*, case-insensitively."""
        allowed = {
            normalized if normalized.startswith(".") else f".{normalized}"
            for extension in extensions
            if (normalized := extension.strip().lower())
        }
        return [item for item in files if item["extension"].lower() in allowed]

    @staticmethod
    def get_statistics(files: Iterable[dict[str, Any]]) -> dict[str, Any]:
        """Calculate summary values expected by ``cli.py``."""
        items = list(files)
        total_size = sum(item["size_bytes"] for item in items)
        by_extension = Counter(item["extension"] for item in items)
        largest = max(items, key=lambda item: item["size_bytes"], default=None)
        return {
            "total_files": len(items),
            "total_size_mb": total_size / (1024 * 1024),
            "by_extension": dict(sorted(by_extension.items())),
            "largest_file": largest,
        }

    def _is_hidden(self, path: Path) -> bool:
        try:
            if any(part.startswith(".") for part in path.relative_to(self.root).parts):
                return True
        except ValueError:
            if path.name.startswith("."):
                return True
        try:
            attributes = getattr(path.stat(), "st_file_attributes", 0)
            return bool(attributes & 0x2)  # FILE_ATTRIBUTE_HIDDEN on Windows
        except OSError:
            return True


class FileDuplicateFinder:
    """Find byte-identical files using a size prefilter and SHA-256 hashes."""

    def find_duplicates(
        self, files: Iterable[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        """Return only hash groups containing two or more readable files."""
        by_size: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for item in files:
            by_size[item["size_bytes"]].append(item)

        duplicates: dict[str, list[dict[str, Any]]] = {}
        for size, candidates in by_size.items():
            if len(candidates) < 2:
                continue
            by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for item in candidates:
                try:
                    by_hash[self._hash_file(Path(item["path"]))].append(item)
                except OSError:
                    continue
            for digest, group in by_hash.items():
                if len(group) > 1:
                    duplicates[f"sha256:{digest} ({size} bytes)"] = group
        return duplicates

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
