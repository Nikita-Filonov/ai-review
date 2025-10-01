from typing import Optional

from pydantic import BaseModel, RootModel


class GitHubPRReviewSchema(BaseModel):
    id: int
    body: Optional[str] = None
    state: str


class GitHubGetPRReviewsQuerySchema(BaseModel):
    per_page: int


class GitHubGetPRReviewsResponseSchema(RootModel[list[GitHubPRReviewSchema]]):
    root: list[GitHubPRReviewSchema]
