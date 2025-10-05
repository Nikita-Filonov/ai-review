from typing import Optional

from pydantic import BaseModel, RootModel


class GitHubPRReviewSchema(BaseModel):
    id: int
    body: Optional[str] = None
    state: str


class GitHubGetPRReviewsQuerySchema(BaseModel):
    page: int = 1
    per_page: int = 100


class GitHubGetPRReviewsResponseSchema(RootModel[list[GitHubPRReviewSchema]]):
    root: list[GitHubPRReviewSchema]
