from pydantic import BaseModel, Field, ConfigDict

from ai_review.clients.bitbucket_server.pr.schema.user import BitbucketServerUserSchema


class BitbucketServerProjectSchema(BaseModel):
    key: str


class BitbucketServerRepositorySchema(BaseModel):
    slug: str
    name: str
    project: BitbucketServerProjectSchema


class BitbucketServerRefSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    display_id: str = Field(alias="displayId")
    latest_commit: str = Field(alias="latestCommit")
    repository: BitbucketServerRepositorySchema


class BitbucketServerParticipantSchema(BaseModel):
    user: BitbucketServerUserSchema
    role: str
    approved: bool | None = None
    status: str | None = None


class BitbucketServerGetPRResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    version: int | None = None
    title: str
    description: str | None = None
    state: str
    open: bool
    locked: bool
    author: BitbucketServerParticipantSchema
    reviewers: list[BitbucketServerParticipantSchema] = Field(default_factory=list)
    from_ref: BitbucketServerRefSchema = Field(alias="fromRef")
    to_ref: BitbucketServerRefSchema = Field(alias="toRef")
    created_date: int = Field(alias="createdDate")
    updated_date: int = Field(alias="updatedDate")
    links: dict | None = None
