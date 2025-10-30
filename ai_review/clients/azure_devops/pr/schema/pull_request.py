from typing import Any
from pydantic import BaseModel, Field, RootModel


class AzureDevOpsIdentityRefSchema(BaseModel):
    id: str = ""
    display_name: str = Field(default="", alias="displayName")
    unique_name: str = Field(default="", alias="uniqueName")


class AzureDevOpsGitRefSchema(BaseModel):
    name: str = ""
    object_id: str = Field(default="", alias="objectId")


class AzureDevOpsRepositorySchema(BaseModel):
    id: str = ""
    name: str = ""


class AzureDevOpsLabelSchema(BaseModel):
    id: str = ""
    name: str = ""
    active: bool = True


class AzureDevOpsPullRequestSchema(BaseModel):
    pull_request_id: int = Field(alias="pullRequestId")
    title: str = ""
    description: str = ""
    status: str = ""
    created_by: AzureDevOpsIdentityRefSchema = Field(default_factory=AzureDevOpsIdentityRefSchema, alias="createdBy")
    reviewers: list[AzureDevOpsIdentityRefSchema] = Field(default_factory=list)
    labels: list[AzureDevOpsLabelSchema] = Field(default_factory=list)
    source_ref_name: str = Field(default="", alias="sourceRefName")
    target_ref_name: str = Field(default="", alias="targetRefName")
    last_merge_source_commit: dict[str, Any] | None = Field(default=None, alias="lastMergeSourceCommit")
    last_merge_target_commit: dict[str, Any] | None = Field(default=None, alias="lastMergeTargetCommit")
    repository: AzureDevOpsRepositorySchema = Field(default_factory=AzureDevOpsRepositorySchema)


class AzureDevOpsGetPRResponseSchema(AzureDevOpsPullRequestSchema):
    pass

