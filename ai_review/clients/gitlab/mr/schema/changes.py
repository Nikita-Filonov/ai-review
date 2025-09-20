from pydantic import BaseModel, Field


class GitLabUserSchema(BaseModel):
    id: int
    name: str
    username: str


class GitLabDiffRefsSchema(BaseModel):
    base_sha: str
    head_sha: str
    start_sha: str


class GitLabMRChangeSchema(BaseModel):
    diff: str
    old_path: str
    new_path: str


class GitLabGetMRChangesResponseSchema(BaseModel):
    id: int
    iid: int
    title: str
    author: GitLabUserSchema
    labels: list[str] = []
    changes: list[GitLabMRChangeSchema]
    assignees: list[GitLabUserSchema] = Field(default_factory=list)
    reviewers: list[GitLabUserSchema] = Field(default_factory=list)
    diff_refs: GitLabDiffRefsSchema
    project_id: int
    description: str
    source_branch: str
    target_branch: str
