from typing import Protocol

from ai_review.clients.azure_devops.pr.schema.files import AzureDevOpsGetPRFilesResponseSchema
from ai_review.clients.azure_devops.pr.schema.pull_request import AzureDevOpsGetPRResponseSchema
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsGetPRThreadsResponseSchema,
    AzureDevOpsCreatePRThreadRequestSchema,
    AzureDevOpsCreatePRThreadResponseSchema,
    AzureDevOpsCreatePRCommentRequestSchema,
    AzureDevOpsCreatePRCommentResponseSchema,
)


class AzureDevOpsPullRequestsHTTPClientProtocol(Protocol):
    async def get_pull_request(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
    ) -> AzureDevOpsGetPRResponseSchema: ...

    async def get_files(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            iteration_id: int,
    ) -> AzureDevOpsGetPRFilesResponseSchema: ...

    async def get_threads(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
    ) -> AzureDevOpsGetPRThreadsResponseSchema: ...

    async def create_thread(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            request: AzureDevOpsCreatePRThreadRequestSchema,
    ) -> AzureDevOpsCreatePRThreadResponseSchema: ...

    async def create_comment(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            thread_id: int,
            request: AzureDevOpsCreatePRCommentRequestSchema,
    ) -> AzureDevOpsCreatePRCommentResponseSchema: ...
