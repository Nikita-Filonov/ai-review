from httpx import Response, QueryParams

from ai_review.clients.azure_devops.pr.schema.pull_request import AzureDevOpsGetPRResponseSchema
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsGetThreadsResponseSchema,
    AzureDevOpsCreateThreadRequestSchema,
    AzureDevOpsThreadSchema,
    AzureDevOpsCreateCommentRequestSchema,
    AzureDevOpsCommentSchema
)
from ai_review.clients.azure_devops.pr.schema.files import AzureDevOpsPRChangesSchema, AzureDevOpsGetPRFilesResponseSchema
from ai_review.clients.azure_devops.pr.types import AzureDevOpsPullRequestsHTTPClientProtocol
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error


class AzureDevOpsPullRequestsHTTPClientError(HTTPClientError):
    pass


class AzureDevOpsPullRequestsHTTPClient(HTTPClient, AzureDevOpsPullRequestsHTTPClientProtocol):
    API_VERSION = "7.0"

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def get_pull_request_api(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> Response:
        url = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}"
        return await self.get(url, query=QueryParams({"api-version": self.API_VERSION}))

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def get_threads_api(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> Response:
        url = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads"
        return await self.get(url, query=QueryParams({"api-version": self.API_VERSION}))

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def get_files_api(
        self,
        organization: str,
        project: str,
        repository_id: str,
        commit_id: str
    ) -> Response:
        # Get files changed in a specific commit - requires repository scope
        url = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/commits/{commit_id}/changes"
        return await self.get(url, query=QueryParams({"api-version": self.API_VERSION}))

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def create_thread_api(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str,
        request: AzureDevOpsCreateThreadRequestSchema
    ) -> Response:
        url = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads?api-version={self.API_VERSION}"
        return await self.post(url, json=request.model_dump(by_alias=True))

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def create_comment_api(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str,
        thread_id: int,
        request: AzureDevOpsCreateCommentRequestSchema
    ) -> Response:
        url = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads/{thread_id}/comments?api-version={self.API_VERSION}"
        return await self.post(url, json=request.model_dump(by_alias=True))

    async def get_pull_request(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> AzureDevOpsGetPRResponseSchema:
        response = await self.get_pull_request_api(organization, project, repository_id, pull_request_id)
        return AzureDevOpsGetPRResponseSchema.model_validate_json(response.text)

    async def get_threads(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> AzureDevOpsGetThreadsResponseSchema:
        response = await self.get_threads_api(organization, project, repository_id, pull_request_id)
        data = response.json()
        threads = data.get("value", [])
        return AzureDevOpsGetThreadsResponseSchema(root=threads)

    async def get_changes(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str
    ) -> AzureDevOpsPRChangesSchema:
        # First get PR to get the last commit
        pr = await self.get_pull_request(organization, project, repository_id, pull_request_id)
        
        # Get changes from the last source commit
        commit_id = pr.last_merge_source_commit.get("commitId", "")
        if not commit_id:
            return AzureDevOpsPRChangesSchema(changes=[])
        
        response = await self.get_files_api(organization, project, repository_id, commit_id)
        data = response.json()
        
        # Azure DevOps returns changes in 'changes' field from commits API
        changes_list = data.get("changes", [])
        return AzureDevOpsPRChangesSchema(changes=changes_list)
    
    async def get_files(
        self,
        organization: str,
        project: str,
        repository_id: str,
        commit_id: str
    ) -> AzureDevOpsGetPRFilesResponseSchema:
        response = await self.get_files_api(organization, project, repository_id, commit_id)
        data = response.json()
        files = data.get("changes", [])
        return AzureDevOpsGetPRFilesResponseSchema(count=len(files), value=files)

    async def create_thread(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str,
        request: AzureDevOpsCreateThreadRequestSchema
    ) -> AzureDevOpsThreadSchema:
        response = await self.create_thread_api(organization, project, repository_id, pull_request_id, request)
        return AzureDevOpsThreadSchema.model_validate_json(response.text)
    
    async def create_thread_with_dict(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str,
        request_dict: dict
    ) -> AzureDevOpsThreadSchema:
        """Create thread using dict directly to avoid Pydantic serialization issues"""
        url = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads?api-version={self.API_VERSION}"
        response = await self.post(url, json=request_dict)
        return AzureDevOpsThreadSchema.model_validate_json(response.text)

    async def create_comment(
        self,
        organization: str,
        project: str,
        repository_id: str,
        pull_request_id: str,
        thread_id: int,
        request: AzureDevOpsCreateCommentRequestSchema
    ) -> AzureDevOpsCommentSchema:
        response = await self.create_comment_api(organization, project, repository_id, pull_request_id, thread_id, request)
        return AzureDevOpsCommentSchema.model_validate_json(response.text)

