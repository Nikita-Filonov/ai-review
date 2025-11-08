from pydantic import BaseModel, Field, ConfigDict

from ai_review.clients.bitbucket_cloud.pr.schema.user import BitbucketCloudUserSchema


class BitbucketCloudCommentContentSchema(BaseModel):
    raw: str
    html: str | None = None
    markup: str | None = None


class BitbucketCloudCommentInlineSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: str
    to_line: int | None = Field(alias="to", default=None)
    from_line: int | None = Field(alias="from", default=None)


class BitbucketCloudCommentParentSchema(BaseModel):
    id: int


class BitbucketCloudPRCommentSchema(BaseModel):
    id: int
    user: BitbucketCloudUserSchema | None = None
    parent: BitbucketCloudCommentParentSchema | None = None
    inline: BitbucketCloudCommentInlineSchema | None = None
    content: BitbucketCloudCommentContentSchema


class BitbucketCloudGetPRCommentsQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    page: int = 1
    page_len: int = Field(alias="pagelen", default=100)


class BitbucketCloudGetPRCommentsResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    page: int | None = None
    next: str | None = None
    values: list[BitbucketCloudPRCommentSchema]
    page_len: int = Field(alias="pagelen")


class BitbucketCloudCreatePRCommentRequestSchema(BaseModel):
    parent: BitbucketCloudCommentParentSchema | None = None
    inline: BitbucketCloudCommentInlineSchema | None = None
    content: BitbucketCloudCommentContentSchema


class BitbucketCloudCreatePRCommentResponseSchema(BaseModel):
    id: int
    parent: BitbucketCloudCommentParentSchema | None = None
    inline: BitbucketCloudCommentInlineSchema | None = None
    content: BitbucketCloudCommentContentSchema
