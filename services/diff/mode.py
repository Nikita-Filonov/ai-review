from typing import Callable

from config import settings
from libs.config.review import ReviewMode


def full_file_filter(line_no: int, changed: set[int]) -> bool:
    return True


def only_changed_filter(line_no: int, changed: set[int]) -> bool:
    return line_no in changed


def changed_with_context_filter(line_no: int, changed: set[int]) -> bool:
    context = max(0, settings.review.context_lines)
    return any(abs(line_no - c) <= context for c in changed)


MAP_REVIEW_MODE: dict[ReviewMode, Callable[[int, set[int]], bool]] = {
    ReviewMode.FULL_FILE: full_file_filter,
    ReviewMode.ONLY_CHANGED: only_changed_filter,
    ReviewMode.CHANGED_WITH_CONTEXT: changed_with_context_filter
}
