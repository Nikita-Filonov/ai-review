from pydantic import BaseModel, Field, ConfigDict

from ai_review.clients.bitbucket.pr.schema.user import BitbucketUserSchema


class BitbucketCommentContentSchema(BaseModel):
    raw: str
    html: str | None = None
    markup: str | None = None


class BitbucketCommentInlineSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: str
    to_line: int | None = Field(alias="to", default=None)
    from_line: int | None = Field(alias="from", default=None)


class BitbucketCommentParentSchema(BaseModel):
    id: int


class BitbucketPRCommentSchema(BaseModel):
    id: int
    user: BitbucketUserSchema | None = None
    parent: BitbucketCommentParentSchema | None = None
    inline: BitbucketCommentInlineSchema | None = None
    content: BitbucketCommentContentSchema


class BitbucketGetPRCommentsQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    page: int = 1
    page_len: int = Field(alias="pagelen", default=100)


class BitbucketGetPRCommentsResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int
    page: int | None = None
    next: str | None = None
    values: list[BitbucketPRCommentSchema]
    page_len: int = Field(alias="pagelen")


class BitbucketParentSchema(BaseModel):
    id: int


class BitbucketCreatePRCommentRequestSchema(BaseModel):
    parent: BitbucketParentSchema | None = None
    inline: BitbucketCommentInlineSchema | None = None
    content: BitbucketCommentContentSchema


class BitbucketCreatePRCommentResponseSchema(BaseModel):
    id: int
    parent: BitbucketParentSchema | None = None
    inline: BitbucketCommentInlineSchema | None = None
    content: BitbucketCommentContentSchema
