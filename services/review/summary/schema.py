from pydantic import BaseModel, field_validator


class SummaryCommentSchema(BaseModel):
    text: str

    @field_validator("text")
    def normalize_text(cls, value: str) -> str:
        return (value or "").strip()
