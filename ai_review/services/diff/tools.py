from pathlib import Path

from ai_review.config import settings
from ai_review.libs.diff.models import Diff, DiffFile, DiffLineType
from ai_review.libs.logger import get_logger
from ai_review.services.git.service import GitService

logger = get_logger("DIFF_TOOLS")


def normalize_file_path(file_path: str) -> str:
    """Normalize a git diff file path (remove a/ b/ prefixes, convert slashes)."""
    if not file_path:
        return ""

    file_path = file_path.replace("\\", "/").lstrip("./")
    if file_path.startswith("a/") or file_path.startswith("b/"):
        return file_path[2:]

    return file_path


def find_diff_file(diff: Diff, file_path: str) -> DiffFile | None:
    target = normalize_file_path(file_path)
    for file in diff.files:
        if normalize_file_path(file.new_name) == target or normalize_file_path(file.orig_name) == target:
            return file

    return None


def read_snapshot(file_path: str, *, base_sha: str | None = None, head_sha: str | None = None) -> str | None:
    git = GitService()
    try:
        if head_sha:
            text = git.get_file_at_commit(file_path, head_sha)
            if text is not None:
                return text

        if base_sha:
            text = git.get_file_at_commit(file_path, base_sha)
            if text is not None:
                return text
    except Exception as e:
        logger.warning(f"Git snapshot read failed for {file_path}: {e}")

    try:
        return Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Workspace read failed for {file_path}: {e}")
        return None


def marker_for_line(line_type: DiffLineType | None = None, *, added: bool = False, removed: bool = False) -> str:
    if (line_type is DiffLineType.ADDED) or added:
        return settings.review.review_added_marker
    if (line_type is DiffLineType.REMOVED) or removed:
        return settings.review.review_removed_marker
    return ""
