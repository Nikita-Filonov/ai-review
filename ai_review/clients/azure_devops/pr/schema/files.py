from pydantic import BaseModel, Field, ConfigDict, field_validator


class AzureDevOpsFilePositionSchema(BaseModel):
    """Represents a specific position in a file (line and offset)."""
    model_config = ConfigDict(populate_by_name=True)

    line: int | None = Field(default=None)
    offset: int | None = Field(default=None)
    column: int | None = Field(default=None)


class AzureDevOpsPRItemSchema(BaseModel):
    """Represents a file or item in a PR change entry."""
    model_config = ConfigDict(populate_by_name=True)

    path: str
    object_id: str = Field(alias="objectId")

    @field_validator("path")
    def normalize_path(cls, value: str) -> str:
        return value.lstrip("/")


class AzureDevOpsPRChangeSchema(BaseModel):
    """Represents a single file change within a PR iteration."""
    model_config = ConfigDict(populate_by_name=True)

    item: AzureDevOpsPRItemSchema
    change_type: str = Field(alias="changeType")


class AzureDevOpsGetPRFilesQuerySchema(BaseModel):
    """Query params for fetching changed files in a PR iteration."""
    model_config = ConfigDict(populate_by_name=True)

    top: int = 100
    continuation_token: list[str] | None = Field(alias="continuationToken", default=None)


class AzureDevOpsGetPRFilesResponseSchema(BaseModel):
    """Response model for listing files changed in a PR iteration."""
    model_config = ConfigDict(populate_by_name=True)

    count: int | None = None
    change_entries: list[AzureDevOpsPRChangeSchema] = Field(alias="changeEntries")
    continuation_token: list[str] | None = Field(alias="continuationToken", default=None)
