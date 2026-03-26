from pydantic import BaseModel, field_validator

from ai_review.config import settings


class SummaryCommentSchema(BaseModel):
    text: str

    @field_validator("text")
    def normalize_text(cls, value: str) -> str:
        return (value or "").strip()

    @property
    def body_with_tag(self) -> str:
        return f"{self.text}\n\n{settings.review.summary_tag}"

    @property
    def body_with_fallback_tag(self) -> str:
        return f"{self.text}\n\n{settings.review.inline_fallback_tag}"
