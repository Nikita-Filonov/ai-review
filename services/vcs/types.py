from typing import Protocol

from pydantic import BaseModel


class MRInfoSchema(BaseModel):
    title: str
    base_sha: str
    head_sha: str
    start_sha: str
    description: str
    changed_files: list[str]


class MRNoteSchema(BaseModel):
    id: int | str
    body: str


class MRDiscussionSchema(BaseModel):
    id: str
    notes: list[MRNoteSchema]


class VCSClient(Protocol):
    async def get_mr_info(self) -> MRInfoSchema:
        ...

    async def get_discussions(self) -> list[MRDiscussionSchema]:
        ...

    async def create_comment(self, message: str) -> None:
        ...

    async def create_discussion(self, file: str, line: int, message: str) -> None:
        ...
