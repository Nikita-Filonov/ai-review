from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class FileMode(Enum):
    DELETED = auto()
    MODIFIED = auto()
    NEW = auto()


class DiffLineType(Enum):
    ADDED = auto()
    REMOVED = auto()
    UNCHANGED = auto()


@dataclass
class DiffLine:
    type: DiffLineType
    number: int | None
    content: str
    position: int


@dataclass
class DiffRange:
    start: int
    length: int
    lines: List[DiffLine]


@dataclass
class DiffHunk:
    header: str
    orig_range: DiffRange
    new_range: DiffRange
    lines: List[DiffLine]


@dataclass
class DiffFile:
    header: str
    mode: FileMode
    orig_name: str
    new_name: str
    hunks: List[DiffHunk]

    def added_new_lines(self) -> list[DiffLine]:
        return [
            line
            for hunk in self.hunks
            for line in hunk.new_range.lines
            if line.type is DiffLineType.ADDED
        ]

    def removed_old_lines(self) -> list[DiffLine]:
        return [
            line
            for hunk in self.hunks
            for line in hunk.orig_range.lines
            if line.type is DiffLineType.REMOVED
        ]

    def added_line_numbers(self) -> set[int]:
        return {line.number for line in self.added_new_lines() if line.number is not None}

    def removed_line_numbers(self) -> set[int]:
        return {line.number for line in self.removed_old_lines() if line.number is not None}


@dataclass
class Diff:
    files: List[DiffFile]
    raw: str

    def summary(self) -> str:
        parts = []
        for file in self.files:
            parts.append(f"{file.mode.name} {file.new_name or file.orig_name}")
            for hunk in file.hunks:
                parts.append(f"  Hunk: {hunk.header} ({len(hunk.lines)} lines)")

        return "\n".join(parts)

    def changed_lines(self) -> dict[str, list[int]]:
        result: dict[str, list[int]] = {}
        for file in self.files:
            if file.mode == FileMode.DELETED:
                continue

            result[file.new_name] = [
                line.number for h in file.hunks for line in h.new_range.lines
                if line.type == DiffLineType.ADDED
            ]

        return result

    def changed_files(self) -> list[str]:
        return [file.new_name for file in self.files if file.mode != FileMode.DELETED]
