from typing import Protocol

from ai_review.clients.azure_devops.pr.schema.pull_request import AzureDevOpsGetPRResponseSchema
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsGetThreadsResponseSchema,
    AzureDevOpsCreateThreadRequestSchema,
    AzureDevOpsThreadSchema,
    AzureDevOpsCreateCommentRequestSchema,
    AzureDevOpsCommentSchema
)
from ai_review.clients.azure_devops.pr.schema.files import AzureDevOpsPRChangesSchema, AzureDevOpsGetPRFilesResponseSchema, AzureDevOpsGetPRFilesResponseSchema


class AzureDevOpsPullRequestsHTTPClientProtocol(Protocol):
    async def get_pull_request(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> AzureDevOpsGetPRResponseSchema:
        ...

    async def get_threads(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> AzureDevOpsGetThreadsResponseSchema:
        ...

    async def get_changes(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> AzureDevOpsPRChangesSchema:
        ...
    
    async def get_files(
        self,
        organization: str,
        project: str,
        repository_id: str,
        commit_id: str
    ) -> AzureDevOpsGetPRFilesResponseSchema:
        ...
    
    async def get_files(
        self,
        organization: str,
        project: str,
        commit_id: str
    ) -> AzureDevOpsGetPRFilesResponseSchema:
        ...

    async def create_thread(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str,
        request: AzureDevOpsCreateThreadRequestSchema
    ) -> AzureDevOpsThreadSchema:
        ...

    async def create_comment(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str,
        thread_id: int,
        request: AzureDevOpsCreateCommentRequestSchema
    ) -> AzureDevOpsCommentSchema:
        ...

