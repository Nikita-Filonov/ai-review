from typing import Protocol

from pydantic import BaseModel, Field


class MRUserSchema(BaseModel):
    name: str = ""
    username: str = ""


class MRInfoSchema(BaseModel):
    title: str = ""
    author: MRUserSchema = Field(default_factory=MRUserSchema)
    labels: list[str] = Field(default_factory=list)
    base_sha: str = ""
    head_sha: str = ""
    assignees: list[MRUserSchema] = Field(default_factory=list)
    reviewers: list[MRUserSchema] = Field(default_factory=list)
    start_sha: str = ""
    description: str = ""
    source_branch: str = ""
    target_branch: str = ""
    changed_files: list[str] = Field(default_factory=list)


class MRNoteSchema(BaseModel):
    id: int | str
    body: str


class MRDiscussionSchema(BaseModel):
    id: str
    notes: list[MRNoteSchema]


class MRCommentSchema(BaseModel):
    id: int | str
    body: str


class VCSClient(Protocol):
    async def get_mr_info(self) -> MRInfoSchema:
        ...

    async def get_comments(self) -> list[MRCommentSchema]:
        ...

    async def get_discussions(self) -> list[MRDiscussionSchema]:
        ...

    async def create_comment(self, message: str) -> None:
        ...

    async def create_discussion(self, file: str, line: int, message: str) -> None:
        ...
