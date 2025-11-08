from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from ai_review.clients.azure_devops.pr.schema.user import AzureDevOpsUserSchema


class AzureDevOpsCommitSchema(BaseModel):
    """Represents a commit object associated with a PR (e.g., last merge commit)."""
    model_config = ConfigDict(populate_by_name=True)

    commit_id: str = Field(alias="commitId")


class AzureDevOpsRepositorySchema(BaseModel):
    """Represents a repository in Azure DevOps."""
    id: str
    url: str | None = None
    name: str


class AzureDevOpsGetPRResponseSchema(BaseModel):
    """Represents the main Pull Request object returned by Azure DevOps API."""
    model_config = ConfigDict(populate_by_name=True)

    title: str
    status: str | None = None
    reviewers: list[AzureDevOpsUserSchema] = Field(default_factory=list)
    created_by: AzureDevOpsUserSchema = Field(alias="createdBy")
    repository: AzureDevOpsRepositorySchema
    description: str | None = None
    creation_date: datetime | None = Field(alias="creationDate", default=None)
    pull_request_id: int = Field(alias="pullRequestId")
    source_ref_name: str = Field(alias="sourceRefName")
    target_ref_name: str = Field(alias="targetRefName")
    last_merge_commit: AzureDevOpsCommitSchema | None = Field(alias="lastMergeCommit", default=None)
    last_merge_source_commit: AzureDevOpsCommitSchema | None = Field(alias="lastMergeSourceCommit", default=None)
    last_merge_target_commit: AzureDevOpsCommitSchema | None = Field(alias="lastMergeTargetCommit", default=None)
