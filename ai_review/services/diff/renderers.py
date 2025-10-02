"""
Renderers for diff views.

Supported build modes:
- FULL_FILE_CURRENT          snapshot after changes (+ markers for added)
- FULL_FILE_PREVIOUS         snapshot before changes (+ markers for removed)
- FULL_FILE_DIFF             full unified diff (+, -, unchanged)
- ONLY_ADDED                 only added lines
- ONLY_REMOVED               only removed lines
- ADDED_AND_REMOVED          added + removed
- ONLY_ADDED_WITH_CONTEXT    added + surrounding unchanged lines
- ONLY_REMOVED_WITH_CONTEXT  removed + surrounding unchanged lines
- ADDED_AND_REMOVED_WITH_CONTEXT added + removed + surrounding unchanged lines
"""
from enum import Enum
from typing import Iterable

from ai_review.libs.diff.models import DiffFile, DiffLineType
from ai_review.services.diff.tools import normalize_file_path, marker_for_line, read_snapshot


class MarkerType(Enum):
    ADDED = "added"
    REMOVED = "removed"


def build_full_file_current(file: DiffFile | None, file_path: str, head_sha: str | None) -> str:
    text = read_snapshot(file_path, head_sha=head_sha)
    if text is None:
        return f"# Failed to read current snapshot for {file_path}"

    added_new = file.added_line_numbers() if file else set()
    return render_plain_numbered(text.splitlines(), added_new, marker_type=MarkerType.ADDED)


def build_full_file_previous(file: DiffFile | None, file_path: str, base_sha: str | None) -> str:
    text = read_snapshot(file_path, base_sha=base_sha)
    if text is None:
        return f"# Failed to read previous snapshot for {file_path} (base_sha missing or file absent)"

    removed_old = file.removed_line_numbers() if file else set()
    return render_plain_numbered(text.splitlines(), removed_old, marker_type=MarkerType.REMOVED)


def build_full_file_diff(file: DiffFile | None) -> str:
    return render_unified(file, include_added=True, include_removed=True, include_unchanged=True, context=0)


def build_only_added(file: DiffFile | None) -> str:
    return render_unified(file, include_added=True, include_removed=False, include_unchanged=False, context=0)


def build_only_removed(file: DiffFile | None) -> str:
    return render_unified(file, include_added=False, include_removed=True, include_unchanged=False, context=0)


def build_added_and_removed(file: DiffFile | None) -> str:
    return render_unified(file, include_added=True, include_removed=True, include_unchanged=False, context=0)


def build_only_added_with_context(file: DiffFile | None, context: int) -> str:
    return render_unified(file, include_added=True, include_removed=False, include_unchanged=True, context=context)


def build_only_removed_with_context(file: DiffFile | None, context: int) -> str:
    return render_unified(file, include_added=False, include_removed=True, include_unchanged=True, context=context)


def build_added_and_removed_with_context(file: DiffFile | None, context: int) -> str:
    return render_unified(file, include_added=True, include_removed=True, include_unchanged=True, context=context)


def render_plain_numbered(lines: Iterable[str], changed: set[int], marker_type: MarkerType) -> str:
    def choose_marker(line_no: int) -> str:
        if line_no not in changed:
            return ""
        if marker_type is MarkerType.ADDED:
            return marker_for_line(added=True)
        if marker_type is MarkerType.REMOVED:
            return marker_for_line(removed=True)
        return ""

    return "\n".join(
        f"{line_no}: {content}{choose_marker(line_no)}"
        for line_no, content in enumerate(lines, start=1)
    )


def render_unified(
        file: DiffFile | None,
        *,
        include_added: bool,
        include_removed: bool,
        include_unchanged: bool,
        context: int,
) -> str:
    """
    Render unified diff view.

    Each line is prefixed with:
      '+' for added lines,
      '-' for removed lines,
      ' ' for unchanged lines.

    Context controls how many unchanged lines around modifications are shown.
    """
    if file is None:
        return "# Diff target not found"

    if not file.hunks:
        header = normalize_file_path(file.new_name or file.orig_name)
        return f"# No matching lines for mode in {header}"

    lines_out: list[str] = []

    added_new_positions = file.added_line_numbers()
    removed_old_positions = file.removed_line_numbers()

    def in_context(inner_old_no: int | None, inner_new_no: int | None) -> bool:
        """Check if an unchanged line falls within context radius."""
        if context <= 0:
            return False
        if include_added and inner_new_no is not None:
            if any(abs(new_no - a) <= context for a in added_new_positions):
                return True
        if include_removed and inner_old_no is not None:
            if any(abs(old_no - r) <= context for r in removed_old_positions):
                return True
        return False

    for hunk in file.hunks:
        old_no = hunk.orig_range.start
        new_no = hunk.new_range.start

        for line in hunk.lines:
            if line.type is DiffLineType.ADDED:
                if include_added:
                    lines_out.append(f"+{new_no}: {line.content}{marker_for_line(DiffLineType.ADDED)}")
                new_no += 1

            elif line.type is DiffLineType.REMOVED:
                if include_removed:
                    lines_out.append(f"-{old_no}: {line.content}{marker_for_line(DiffLineType.REMOVED)}")
                old_no += 1

            else:
                if include_unchanged and (context == 0 or in_context(old_no, new_no)):
                    lines_out.append(f" {new_no}: {line.content}")
                old_no += 1
                new_no += 1

    if not lines_out:
        header = normalize_file_path(file.new_name or file.orig_name)
        return f"# No matching lines for mode in {header}"

    return "\n".join(lines_out)
