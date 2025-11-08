from pydantic import BaseModel, Field

from ai_review.clients.bitbucket_cloud.pr.schema.user import BitbucketCloudUserSchema


class BitbucketCloudBranchSchema(BaseModel):
    name: str


class BitbucketCloudCommitSchema(BaseModel):
    hash: str


class BitbucketCloudRepositorySchema(BaseModel):
    uuid: str
    full_name: str


class BitbucketCloudPRLocationSchema(BaseModel):
    branch: BitbucketCloudBranchSchema
    commit: BitbucketCloudCommitSchema
    repository: BitbucketCloudRepositorySchema


class BitbucketCloudGetPRResponseSchema(BaseModel):
    id: int
    title: str
    description: str | None = None
    state: str
    author: BitbucketCloudUserSchema
    source: BitbucketCloudPRLocationSchema
    destination: BitbucketCloudPRLocationSchema
    reviewers: list[BitbucketCloudUserSchema] = Field(default_factory=list)
    participants: list[BitbucketCloudUserSchema] = Field(default_factory=list)
