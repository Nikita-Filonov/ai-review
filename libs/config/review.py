from enum import StrEnum

from pydantic import BaseModel, Field


class ReviewMode(StrEnum):
    FULL_FILE = "FULL_FILE"
    ONLY_CHANGED = "ONLY_CHANGED"
    CHANGED_WITH_CONTEXT = "CHANGED_WITH_CONTEXT"


class ReviewConfig(BaseModel):
    mode: ReviewMode = ReviewMode.FULL_FILE
    inline_tag: str = Field(default="#aireview-inline")
    summary_tag: str = Field(default="#aireview-summary")
    context_lines: int = Field(default=10, ge=0)
    allow_changes: list[str] = Field(default_factory=list)
    ignore_changes: list[str] = Field(default_factory=list)
    review_change_marker: str = "# changed"
