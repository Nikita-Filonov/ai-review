from pydantic import BaseModel


class GitLabPositionSchema(BaseModel):
    position_type: str | None = "text"
    base_sha: str | None = None
    head_sha: str | None = None
    start_sha: str | None = None
    old_path: str | None = None
    new_path: str | None = None
    old_line: int | None = None
    new_line: int | None = None
    line_range: dict | None = None
