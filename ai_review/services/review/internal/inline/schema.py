from typing import Self

from pydantic import BaseModel, Field, RootModel, field_validator

from ai_review.config import settings
from ai_review.libs.diff.models import Side

DedupKey = tuple[str, int, Side | None, str]


class InlineCommentSchema(BaseModel):
    file: str = Field(min_length=1)
    line: int = Field(ge=1)
    message: str = Field(min_length=1)
    suggestion: str | None = None
    side: Side | None = None
    """Which file of the diff `line` is numbered in, when the caller knows.

    A removed line is numbered in the old file, so its number can collide with
    an unrelated new-file line and a provider that has to guess anchors the
    comment to the wrong code. `None` means no claim is made, which is all the
    LLM review path can say: it reads a rendered diff and reports a bare number.
    """

    @field_validator("file")
    def normalize_file(cls, value: str) -> str:
        value = value.strip().replace("\\", "/")
        return value.lstrip("/")

    @field_validator("message")
    def normalize_message(cls, value: str) -> str:
        return value.strip()

    @property
    def dedup_key(self) -> DedupKey:
        """Identify the comment by where it points and what it says.

        `side` belongs to the location: the same number on the two sides of a
        change addresses two different lines, so collapsing them would drop a
        finding rather than a duplicate.
        """
        return self.file, self.line, self.side, (self.suggestion or self.message).strip().lower()

    @property
    def body(self) -> str:
        if self.suggestion:
            return f"{self.message}\n\n```suggestion\n{self.suggestion}\n```"

        return self.message

    @property
    def body_with_tag(self) -> str:
        return f"{self.body}\n\n{settings.review.inline_tag}"

    @property
    def fallback_body(self) -> str:
        """Render the comment as a general comment, naming the line in the text.

        A number on the old side would send the reader to whatever now occupies
        that line in the new file, so it is marked. The new side is the reading
        everyone assumes and is left alone.
        """
        if self.side == "old":
            return f"**{self.file}:{self.line} (old side)** — {self.message}"

        return f"**{self.file}:{self.line}** — {self.message}"


class InlineCommentListSchema(RootModel[list[InlineCommentSchema]]):
    root: list[InlineCommentSchema]

    def dedupe(self) -> Self:
        results_map: dict[DedupKey, InlineCommentSchema] = {
            comment.dedup_key: comment for comment in self.root
        }

        return InlineCommentListSchema(root=list(results_map.values()))
