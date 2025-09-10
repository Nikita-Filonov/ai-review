import re

from clients.gitlab.mr.schema.changes import GitLabMRChangeSchema
from services.diff.schema import DiffLineListSchema, DiffLineSchema, DiffLineType

HUNK_RE = re.compile(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


class DiffService:
    @classmethod
    def build_added_diff_line(cls, file: str, line: int, raw: str) -> DiffLineSchema:
        return DiffLineSchema(
            line_type=DiffLineType.ADDED,
            file=file,
            line=line,
            content=raw[1:],
        )

    @classmethod
    def build_deleted_diff_line(cls, file: str, raw: str) -> DiffLineSchema:
        return DiffLineSchema(
            line_type=DiffLineType.DELETED,
            file=file,
            line=None,
            content=raw[1:],
        )

    @classmethod
    def build_unchanged_diff_line(cls, file: str, line: int, raw: str) -> DiffLineSchema:
        return DiffLineSchema(
            line_type=DiffLineType.UNCHANGED,
            file=file,
            line=line,
            content=raw[1:] if raw else "",
        )

    @classmethod
    def build_diff_lines(cls, raw_diff: str, file: str) -> DiffLineListSchema:
        lines: list[DiffLineSchema] = []
        new_line: int | None = None

        for raw_line in raw_diff.splitlines():
            hunk_match = HUNK_RE.match(raw_line)
            if hunk_match:
                new_line = int(hunk_match.group(2))
                continue

            if raw_line == r"\ No newline at end of file":
                continue

            if raw_line.startswith("+") and not raw_line.startswith("+++ "):
                lines.append(cls.build_added_diff_line(file, new_line, raw_line))
                new_line += 1
                continue

            if raw_line.startswith("-") and not raw_line.startswith("--- "):
                lines.append(cls.build_deleted_diff_line(file, raw_line))
                continue

            if new_line is not None:
                lines.append(cls.build_unchanged_diff_line(file, new_line, raw_line))
                new_line += 1

        return DiffLineListSchema(root=lines)

    @classmethod
    def build_allowed_map(cls, changes: list[GitLabMRChangeSchema]) -> dict[str, set[int]]:
        allowed: dict[str, set[int]] = {}

        for change in changes:
            diff_lines = cls.build_diff_lines(change.diff, change.new_path)
            added_lines = diff_lines.filter_only_added()
            if not added_lines.root:
                continue

            allowed[change.new_path] = {
                diff_line.line for diff_line in added_lines.root
                if diff_line.line is not None
            }

        return allowed
