from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field


class ThreadKind(StrEnum):
    INLINE = "INLINE"
    SUMMARY = "SUMMARY"


class UserSchema(BaseModel):
    id: str | int | None = None
    name: str = ""
    username: str = ""


class BranchRefSchema(BaseModel):
    ref: str = ""
    sha: str = ""


class ReviewInfoSchema(BaseModel):
    id: str | int | None = None
    title: str = ""
    description: str = ""
    author: UserSchema = Field(default_factory=UserSchema)
    labels: list[str] = Field(default_factory=list)
    assignees: list[UserSchema] = Field(default_factory=list)
    reviewers: list[UserSchema] = Field(default_factory=list)
    source_branch: BranchRefSchema = Field(default_factory=BranchRefSchema)
    target_branch: BranchRefSchema = Field(default_factory=BranchRefSchema)
    changed_files: list[str] = Field(default_factory=list)
    base_sha: str = ""
    head_sha: str = ""
    start_sha: str = ""


class ReviewCommentSchema(BaseModel):
    id: str | int
    body: str
    file: str | None = None
    line: int | None = None
    author: UserSchema = Field(default_factory=UserSchema)
    parent_id: str | int | None = None
    thread_id: str | int | None = None


class ReviewThreadSchema(BaseModel):
    id: str | int
    kind: ThreadKind
    file: str | None = None
    line: int | None = None
    comments: list[ReviewCommentSchema]


class VCSClientProtocol(Protocol):
    """
    Unified interface for version control system integrations (GitHub, GitLab, Bitbucket, etc.).
    Designed for code review automation: fetching review info, comments, and posting feedback.
    """

    # --- Review info ---
    async def get_review_info(self) -> ReviewInfoSchema:
        """Fetch general information about the current review (PR/MR)."""

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        """Fetch all top-level (non-inline) comments."""

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        """Fetch inline (file + line attached) comments."""

    async def create_general_comment(self, message: str) -> None:
        """Post a top-level comment."""

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        """Post a comment attached to a specific line in file."""

    # --- Replies ---
    async def create_inline_reply(self, thread_id: int | str, message: str) -> None:
        """Reply to an existing inline comment thread."""

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        """Reply to a summary/general comment (flat if VCS doesn't support threads)."""

    # --- Threads ---
    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        """
        Fetch grouped inline comment threads.
        If VCS doesn't support threads natively, group by file+line.
        """

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        """
        Fetch grouped general (summary-level) comment threads.
        If VCS is flat (e.g. GitHub issues), each comment is a separate thread.
        """
