from pydantic import BaseModel

from libs.config.http import HTTPClientConfig


class GitLabPipelineConfig(BaseModel):
    project_id: str
    merge_request_id: str


class GitLabHTTPClientConfig(HTTPClientConfig):
    pass
