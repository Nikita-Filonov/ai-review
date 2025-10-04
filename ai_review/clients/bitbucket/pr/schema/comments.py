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
    pagelen: int = 100


class BitbucketGetPRCommentsResponseSchema(BaseModel):
    size: int
    page: int | None = None
    next: str | None = None
    values: list[BitbucketPRCommentSchema]
    pagelen: int


class BitbucketCreatePRCommentRequestSchema(BaseModel):
    inline: BitbucketCommentInlineSchema | None = None
    content: BitbucketCommentContentSchema


class BitbucketCreatePRCommentResponseSchema(BaseModel):
    id: int
    inline: BitbucketCommentInlineSchema | None = None
    content: BitbucketCommentContentSchema
