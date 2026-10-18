"""Interactive entry point for the FileScanner command-line application."""

from __future__ import annotations

from file_scanner import FileDuplicateFinder, FileScanner
from utils import format_bytes, print_section


class FileAnalysisApp:
    """A compact interactive wrapper around the same safe scan operations as the CLI."""

    def start_interactive(self) -> None:
        print("FileScanner interactive mode. Press Enter without a path to exit.")
        while True:
            path = input("Directory to scan: ").strip()
            if not path:
                return
            try:
                scanner = FileScanner(path)
                files = scanner.scan_directory()
                stats = scanner.get_statistics(files)
                print_section("Scan results")
                print(f"Found {stats['total_files']} files ({format_bytes(stats['total_size_mb'] * 1024 * 1024)}).")
                if input("Find duplicate files? [y/N]: ").strip().lower() in {"y", "yes"}:
                    duplicates = FileDuplicateFinder().find_duplicates(files)
                    print(f"Found {len(duplicates)} duplicate group(s).")
            except (OSError, ValueError) as error:
                print(f"Error: {error}")
