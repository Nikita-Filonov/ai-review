from pydantic import BaseModel, Field, field_validator

from ai_review.config import settings


class InlineCommentReplySchema(BaseModel):
    message: str = Field(min_length=1)
    suggestion: str | None = None

    @field_validator("message")
    def normalize_message(cls, value: str) -> str:
        return value.strip()

    @property
    def body(self) -> str:
        if self.suggestion:
            return f"{self.message}\n\n```suggestion\n{self.suggestion}\n```"

        return self.message

    @property
    def body_with_tag(self) -> str:
        return f"{self.body}\n\n{settings.review.inline_reply_tag}"
