from dataclasses import dataclass
from enum import Enum, auto


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
class DiffLinePosition:
    """
    A diff line addressed on both sides of the change.

    An added line exists only in the new file, a removed line only in the old
    one, and an unchanged line in both. VCS providers that validate a diff
    position need the pair, not just one side.
    """
    type: DiffLineType
    old_line: int | None
    new_line: int | None


@dataclass
class DiffRange:
    start: int
    length: int
    lines: list[DiffLine]


@dataclass
class DiffHunk:
    header: str
    orig_range: DiffRange
    new_range: DiffRange
    lines: list[DiffLine]


@dataclass
class DiffFile:
    header: str
    mode: FileMode
    orig_name: str
    new_name: str
    hunks: list[DiffHunk]

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

    def line_positions(self) -> list[DiffLinePosition]:
        """
        Pair old and new line numbers for every line of every hunk.

        Each hunk is numbered from its own `@@ -a,b +c,d @@` header, so an
        earlier hunk that inserts or deletes lines cannot shift a later one.
        """
        positions: list[DiffLinePosition] = []

        for hunk in self.hunks:
            old_line = hunk.orig_range.start
            new_line = hunk.new_range.start

            for line in hunk.lines:
                if line.type is DiffLineType.ADDED:
                    positions.append(DiffLinePosition(line.type, None, new_line))
                    new_line += 1
                elif line.type is DiffLineType.REMOVED:
                    positions.append(DiffLinePosition(line.type, old_line, None))
                    old_line += 1
                else:
                    positions.append(DiffLinePosition(line.type, old_line, new_line))
                    old_line += 1
                    new_line += 1

        return positions

    def find_line_position(self, line: int) -> DiffLinePosition | None:
        """
        Resolve a bare line number to the diff line it addresses.

        The number is read as a new-file line first, which covers added and
        unchanged lines and matches how the diff is rendered for the model. Only
        if no new-file line matches is it read as the old-file line of a removed
        line, which is the one case that has no new-file number at all.
        """
        positions = self.line_positions()

        for position in positions:
            if position.new_line == line:
                return position

        for position in positions:
            if position.type is DiffLineType.REMOVED and position.old_line == line:
                return position

        return None


@dataclass
class Diff:
    files: list[DiffFile]
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
