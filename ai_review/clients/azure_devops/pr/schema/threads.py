from typing import Any
from pydantic import BaseModel, Field, RootModel


class AzureDevOpsIdentityRefSchema(BaseModel):
    id: str = ""
    display_name: str = Field(default="", alias="displayName")
    unique_name: str = Field(default="", alias="uniqueName")


class AzureDevOpsThreadContextSchema(BaseModel):
    file_path: str = Field(default="", alias="filePath")
    right_file_start: dict[str, Any] = Field(default_factory=dict, alias="rightFileStart")
    right_file_end: dict[str, Any] = Field(default_factory=dict, alias="rightFileEnd")


class AzureDevOpsCommentSchema(BaseModel):
    id: int = 0
    parent_comment_id: int = Field(default=0, alias="parentCommentId")
    content: str = ""
    author: AzureDevOpsIdentityRefSchema = Field(default_factory=AzureDevOpsIdentityRefSchema)
    comment_type: str = Field(default="text", alias="commentType")


class AzureDevOpsThreadSchema(BaseModel):
    id: int = 0
    published_date: str = Field(default="", alias="publishedDate")
    status: str = ""
    thread_context: AzureDevOpsThreadContextSchema | None = Field(default=None, alias="threadContext")
    comments: list[AzureDevOpsCommentSchema] = Field(default_factory=list)
    properties: dict[str, Any] | None = Field(default=None)


class AzureDevOpsGetThreadsResponseSchema(RootModel):
    root: list[AzureDevOpsThreadSchema]


class AzureDevOpsCreateThreadRequestSchema(BaseModel):
    comments: list[dict[str, str]]
    status: str = "active"
    thread_context: dict[str, Any] | None = Field(default=None, alias="threadContext")


class AzureDevOpsCreateCommentRequestSchema(BaseModel):
    content: str
    parent_comment_id: int = Field(default=0, alias="parentCommentId")

