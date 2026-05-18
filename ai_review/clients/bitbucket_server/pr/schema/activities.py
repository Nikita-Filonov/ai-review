from pydantic import BaseModel, Field, ConfigDict

from ai_review.clients.bitbucket_server.pr.schema.comments import BitbucketServerCommentSchema


class BitbucketServerActivitySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    action: str
    comment: BitbucketServerCommentSchema | None = None


class BitbucketServerGetPRActivitiesQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start: int = 0
    limit: int = 100


class BitbucketServerGetPRActivitiesResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    limit: int
    start: int
    values: list[BitbucketServerActivitySchema]
    is_last_page: bool = Field(alias="isLastPage")
    next_page_start: int | None = Field(default=None, alias="nextPageStart")
