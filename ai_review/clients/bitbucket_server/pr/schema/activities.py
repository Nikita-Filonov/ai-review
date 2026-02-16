from pydantic import BaseModel, ConfigDict, Field

from ai_review.clients.bitbucket_server.pr.schema.comments import BitbucketServerCommentSchema


class BitbucketServerGetPRActivitiesQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start: int = 0
    limit: int = 100
    path: str | None = None
    from_type: str | None = Field(default=None, alias="fromType")


class BitbucketServerPRActivitySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: str | None = None
    comment_action: str | None = Field(default=None, alias="commentAction")
    comment: BitbucketServerCommentSchema | None = None


class BitbucketServerGetPRActivitiesResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    limit: int
    start: int
    values: list[BitbucketServerPRActivitySchema]
    is_last_page: bool = Field(alias="isLastPage")
    next_page_start: int | None = Field(default=None, alias="nextPageStart")
