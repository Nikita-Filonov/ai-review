from pydantic import BaseModel, Field, ConfigDict


class BitbucketCommentContentSchema(BaseModel):
    raw: str
    html: str | None = None
    markup: str | None = None


class BitbucketCommentInlineSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: str
    to_line: int | None = Field(alias="to", default=None)
    from_line: int | None = Field(alias="from", default=None)


class BitbucketPRCommentSchema(BaseModel):
    id: int
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


class BitbucketCreatePRCommentRequestSchema(BaseModel):
    inline: BitbucketCommentInlineSchema | None = None
    content: BitbucketCommentContentSchema


class BitbucketCreatePRCommentResponseSchema(BaseModel):
    id: int
    inline: BitbucketCommentInlineSchema | None = None
    content: BitbucketCommentContentSchema
