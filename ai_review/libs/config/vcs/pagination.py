from pydantic import BaseModel, Field


class VCSPaginationConfig(BaseModel):
    per_page: int = Field(default=100, ge=1, le=100)
    max_pages: int = Field(default=5, ge=1)
