from typing import Literal

from pydantic import BaseModel, RootModel

from ai_review.clients.gitea.pr.schema.user import GiteaUserSchema


class GiteaReviewSchema(BaseModel):
    id: int
    body: str | None = None
    user: GiteaUserSchema | None = None


class GiteaReviewCommentSchema(BaseModel):
    id: int
    body: str
    path: str | None = None
    position: int | None = None
    user: GiteaUserSchema | None = None
    pull_request_review_id: int | None = None


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


class GiteaGetReviewsQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GiteaGetReviewsResponseSchema(RootModel[list[GiteaReviewSchema]]):
    root: list[GiteaReviewSchema]


class GiteaGetReviewCommentsQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GiteaGetReviewCommentsResponseSchema(RootModel[list[GiteaReviewCommentSchema]]):
    root: list[GiteaReviewCommentSchema]
