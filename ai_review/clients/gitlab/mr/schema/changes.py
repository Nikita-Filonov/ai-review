from pydantic import BaseModel, Field

from ai_review.clients.gitlab.mr.schema.user import GitLabUserSchema


class GitLabDiffRefsSchema(BaseModel):
    base_sha: str
    head_sha: str
    start_sha: str


class GitLabMRChangeSchema(BaseModel):
    diff: str | None = None
    old_path: str | None = None
    new_path: str | None = None


class GitLabGetMRChangesResponseSchema(BaseModel):
    id: int
    iid: int
    title: str
    author: GitLabUserSchema
    labels: list[str] = Field(default_factory=list)
    changes: list[GitLabMRChangeSchema]
    assignees: list[GitLabUserSchema] = Field(default_factory=list)
    reviewers: list[GitLabUserSchema] = Field(default_factory=list)
    diff_refs: GitLabDiffRefsSchema
    project_id: int
    description: str | None = None
    source_branch: str
    target_branch: str
