from pydantic import BaseModel, Field, ConfigDict


class AzureDevOpsBaseQuerySchema(BaseModel):
    """Base query schema for Azure DevOps API requests."""
    model_config = ConfigDict(populate_by_name=True)

    api_version: str = Field(default="7.0", alias="api-version")
