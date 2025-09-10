from pydantic import BaseModel


class GitLabDiffRefsSchema(BaseModel):
    base_sha: str
    head_sha: str
    start_sha: str


class GitLabMRChangeSchema(BaseModel):
    diff: str
    old_path: str
    new_path: str


class GitLabGetMRChangesResponseSchema(BaseModel):
    changes: list[GitLabMRChangeSchema]
    diff_refs: GitLabDiffRefsSchema
