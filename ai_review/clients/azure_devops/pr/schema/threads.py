from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from ai_review.clients.azure_devops.pr.schema.files import AzureDevOpsFilePositionSchema
from ai_review.clients.azure_devops.pr.schema.user import AzureDevOpsUserSchema


class AzureDevOpsPRCommentSchema(BaseModel):
    """Represents a single comment in a PR thread."""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    author: AzureDevOpsUserSchema | None = None
    content: str | None = Field(default=None)
    is_deleted: bool = Field(alias="isDeleted", default=False)
    published_date: datetime | None = Field(alias="publishedDate", default=None)
    last_updated_date: datetime | None = Field(alias="lastUpdatedDate", default=None)


class AzureDevOpsThreadContextSchema(BaseModel):
    """Represents the code location context for a thread (file path and line)."""
    model_config = ConfigDict(populate_by_name=True)

    file_path: str | None = Field(alias="filePath", default=None)
    right_file_end: AzureDevOpsFilePositionSchema | None = Field(alias="rightFileEnd", default=None)
    right_file_start: AzureDevOpsFilePositionSchema | None = Field(alias="rightFileStart", default=None)


class AzureDevOpsIterationContextSchema(BaseModel):
    """Identifies the iteration range in which a thread applies."""
    model_config = ConfigDict(populate_by_name=True)

    first_comparing_iteration: int = Field(alias="firstComparingIteration")
    second_comparing_iteration: int = Field(alias="secondComparingIteration")


class AzureDevOpsPullRequestThreadContextSchema(BaseModel):
    """Provides iteration context for PR thread binding."""
    model_config = ConfigDict(populate_by_name=True)

    change_tracking_id: int | None = Field(alias="changeTrackingId", default=None)
    iteration_context: AzureDevOpsIterationContextSchema | None = Field(alias="iterationContext", default=None)


class AzureDevOpsPRThreadSchema(BaseModel):
    """Represents a discussion thread in a Pull Request."""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    status: str | None = None
    comments: list[AzureDevOpsPRCommentSchema] = Field(default_factory=list)
    is_deleted: bool = Field(alias="isDeleted", default=False)
    thread_context: AzureDevOpsThreadContextSchema | None = Field(alias="threadContext", default=None)


class AzureDevOpsGetPRThreadsQuerySchema(BaseModel):
    """Pagination and query params for fetching PR threads."""
    model_config = ConfigDict(populate_by_name=True)

    top: int = 100
    continuation_token: list[str] | None = Field(alias="continuationToken", default=None)


class AzureDevOpsGetPRThreadsResponseSchema(BaseModel):
    """Response model for fetching PR threads with comments."""
    model_config = ConfigDict(populate_by_name=True)

    value: list[AzureDevOpsPRThreadSchema]
    count: int | None = None
    continuation_token: list[str] | None = Field(alias="continuationToken", default=None)


class AzureDevOpsCreatePRCommentRequestSchema(BaseModel):
    """Request for creating a new comment inside an existing thread."""
    content: str


class AzureDevOpsCreatePRCommentResponseSchema(BaseModel):
    """Response after creating a comment."""
    id: int
    content: str


class AzureDevOpsCreatePRThreadRequestSchema(BaseModel):
    """Request for creating a new thread with an initial comment."""
    model_config = ConfigDict(populate_by_name=True)

    status: str = "active"
    comments: list[AzureDevOpsCreatePRCommentRequestSchema]
    thread_context: AzureDevOpsThreadContextSchema | None = Field(alias="threadContext", default=None)
    pull_request_thread_context: AzureDevOpsPullRequestThreadContextSchema | None = Field(
        alias="pullRequestThreadContext", default=None
    )


class AzureDevOpsCreatePRThreadResponseSchema(BaseModel):
    """Response after creating a new discussion thread."""
    id: int
    status: str
    comments: list[AzureDevOpsPRCommentSchema]
