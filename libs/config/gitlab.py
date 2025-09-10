from pydantic import BaseModel, HttpUrl, Field


class GitLabPipelineConfig(BaseModel):
    project_id: str = Field(alias="CI_PROJECT_ID")
    commit_sha: str | None = Field(alias="CI_COMMIT_SHA", default=None)
    server_url: HttpUrl = Field(alias="CI_SERVER_URL")
    merge_request_iid: str = Field(alias="CI_MERGE_REQUEST_IID")


class GitLabHTTPClientConfig(BaseModel):
    api_url: HttpUrl
    api_token: str
