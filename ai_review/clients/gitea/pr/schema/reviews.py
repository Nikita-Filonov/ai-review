from typing import Literal

from pydantic import BaseModel


class GiteaReviewInlineCommentSchema(BaseModel):
    path: str
    body: str
    new_position: int | None = None
    old_position: int | None = None


class GiteaCreateReviewRequestSchema(BaseModel):
    body: str | None = None
    event: Literal["COMMENT"] = "COMMENT"
    comments: list[GiteaReviewInlineCommentSchema]
    commit_id: str | None = None


class GiteaCreateReviewResponseSchema(BaseModel):
    id: int
