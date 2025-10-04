from pydantic import BaseModel
from typing import List, Optional


class BitbucketPRFilePathSchema(BaseModel):
    path: str


class BitbucketPRFileSchema(BaseModel):
    new: BitbucketPRFilePathSchema | None = None
    old: BitbucketPRFilePathSchema | None = None
    status: str
    lines_added: int
    lines_removed: int


class BitbucketGetPRFilesQuerySchema(BaseModel):
    pagelen: int = 100


class BitbucketGetPRFilesResponseSchema(BaseModel):
    size: int
    page: int | None = None
    next: str | None = None
    values: list[BitbucketPRFileSchema]
    pagelen: int
