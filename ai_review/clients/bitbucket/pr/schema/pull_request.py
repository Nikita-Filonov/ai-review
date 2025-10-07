from pydantic import BaseModel, Field

from ai_review.clients.bitbucket.pr.schema.user import BitbucketUserSchema


class BitbucketBranchSchema(BaseModel):
    name: str


class BitbucketCommitSchema(BaseModel):
    hash: str


class BitbucketRepositorySchema(BaseModel):
    uuid: str
    full_name: str


class BitbucketPRLocationSchema(BaseModel):
    branch: BitbucketBranchSchema
    commit: BitbucketCommitSchema
    repository: BitbucketRepositorySchema


class BitbucketGetPRResponseSchema(BaseModel):
    id: int
    title: str
    description: str | None = None
    state: str
    author: BitbucketUserSchema
    source: BitbucketPRLocationSchema
    destination: BitbucketPRLocationSchema
    reviewers: list[BitbucketUserSchema] = Field(default_factory=list)
    participants: list[BitbucketUserSchema] = Field(default_factory=list)
