import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from file_scanner import FileDuplicateFinder, FileScanner


class FileScannerTests(TestCase):
    def test_scan_statistics_filter_and_duplicates(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            tmp_path = Path(temporary_directory)
            (tmp_path / "a.txt").write_text("same", encoding="utf-8")
            (tmp_path / "b.txt").write_text("same", encoding="utf-8")
            (tmp_path / "image.bin").write_bytes(b"different")
            (tmp_path / ".hidden.txt").write_text("hidden", encoding="utf-8")

            scanner = FileScanner(str(tmp_path))
            files = scanner.scan_directory()

            self.assertEqual({item["name"] for item in files}, {"a.txt", "b.txt", "image.bin"})
            self.assertEqual(len(scanner.filter_by_extension(files, ["txt"])), 2)
            stats = scanner.get_statistics(files)
            self.assertEqual(stats["total_files"], 3)
            self.assertEqual(stats["by_extension"], {".bin": 1, ".txt": 2})

            duplicate_groups = FileDuplicateFinder().find_duplicates(files)
            self.assertEqual(len(duplicate_groups), 1)
            self.assertEqual(
                {item["name"] for group in duplicate_groups.values() for item in group},
                {"a.txt", "b.txt"},
            )
            json.dumps({"summary": stats, "files": files, "duplicates": duplicate_groups})
