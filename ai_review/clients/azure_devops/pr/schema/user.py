from pydantic import BaseModel, Field, ConfigDict


class AzureDevOpsUserSchema(BaseModel):
    """Represents a user (author, reviewer, etc.) in Azure DevOps."""
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    url: str | None = None
    image_url: str | None = Field(alias="imageUrl", default=None)
    unique_name: str | None = Field(alias="uniqueName", default=None)
    display_name: str | None = Field(alias="displayName", default=None)
