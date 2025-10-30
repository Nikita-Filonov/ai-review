from pydantic import BaseModel, Field, RootModel


class AzureDevOpsChangeSchema(BaseModel):
    item: dict[str, str | bool] = Field(default_factory=dict)
    change_type: str = Field(default="", alias="changeType")


class AzureDevOpsPRChangesSchema(BaseModel):
    changes: list[AzureDevOpsChangeSchema] = Field(default_factory=list)


class AzureDevOpsFileSchema(BaseModel):
    object_id: str = Field(default="", alias="objectId")
    git_object_type: str = Field(default="", alias="gitObjectType")
    commit_id: str = Field(default="", alias="commitId")
    path: str = ""
    url: str = ""


class AzureDevOpsGetPRFilesResponseSchema(BaseModel):
    count: int = 0
    value: list[AzureDevOpsFileSchema] = Field(default_factory=list)

