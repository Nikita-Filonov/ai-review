from enum import StrEnum

from pydantic import BaseModel, Field


class ReviewMode(StrEnum):
    FULL_FILE_DIFF = "FULL_FILE_DIFF"
    FULL_FILE_CURRENT = "FULL_FILE_CURRENT"
    FULL_FILE_PREVIOUS = "FULL_FILE_PREVIOUS"

    ONLY_ADDED = "ONLY_ADDED"
    ONLY_REMOVED = "ONLY_REMOVED"
    ADDED_AND_REMOVED = "ADDED_AND_REMOVED"

    ONLY_ADDED_WITH_CONTEXT = "ONLY_ADDED_WITH_CONTEXT"
    ONLY_REMOVED_WITH_CONTEXT = "ONLY_REMOVED_WITH_CONTEXT"
    ADDED_AND_REMOVED_WITH_CONTEXT = "ADDED_AND_REMOVED_WITH_CONTEXT"


class ReviewConfig(BaseModel):
    mode: ReviewMode = ReviewMode.FULL_FILE_DIFF
    dry_run: bool = False
    inline_tag: str = Field(
        default="#ai-review-inline",
        description="Marker appended to generated inline comments and replies",
    )
    inline_reply_tag: str = Field(
        default="#ai-review-inline-reply",
        description="Request tag on the latest inline comment; must differ from inline_tag",
    )
    inline_fallback_tag: str = Field(default="#ai-review-inline-fallback")
    summary_tag: str = Field(
        default="#ai-review-summary",
        description="Marker appended to generated summary comments and replies",
    )
    summary_reply_tag: str = Field(
        default="#ai-review-summary-reply",
        description="Request tag on the latest summary comment; must differ from summary_tag",
    )
    context_lines: int = Field(default=10, ge=0)
    allow_changes: list[str] = Field(default_factory=list)
    ignore_changes: list[str] = Field(default_factory=list)
    ignore_pure_renames: bool = True
    review_added_marker: str = " # added"
    review_removed_marker: str = " # removed"
    max_inline_comments: int | None = None
    max_context_comments: int | None = None
    inline_comment_fallback: bool = True
