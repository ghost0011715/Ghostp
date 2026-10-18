"""Small presentation helpers used by the command-line interface."""

from __future__ import annotations

from typing import Any, Iterable


def format_bytes(size: int | float) -> str:
    """Format a byte count for a terminal without losing very small values."""
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(value) < 1024 or unit == "PB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} PB"


def print_section(title: str) -> None:
    """Print a consistently readable terminal section heading."""
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def print_table(rows: Iterable[dict[str, Any]]) -> None:
    """Print dictionaries as a simple dependency-free table."""
    items = list(rows)
    if not items:
        print("(no files)")
        return
    columns = list(items[0])
    widths = {
        column: max(len(column), *(len(str(row.get(column, ""))) for row in items))
        for column in columns
    }
    print("  ".join(column.ljust(widths[column]) for column in columns))
    print("  ".join("-" * widths[column] for column in columns))
    for row in items:
        print("  ".join(str(row.get(column, "")).ljust(widths[column]) for column in columns))
