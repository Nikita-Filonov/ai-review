from httpx import Response, QueryParams

from ai_review.clients.azure_devops.pr.schema.files import (
    AzureDevOpsPRChangeSchema,
    AzureDevOpsGetPRFilesQuerySchema,
    AzureDevOpsGetPRFilesResponseSchema,
)
from ai_review.clients.azure_devops.pr.schema.pull_request import AzureDevOpsGetPRResponseSchema
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsPRThreadSchema,
    AzureDevOpsGetPRThreadsQuerySchema,
    AzureDevOpsGetPRThreadsResponseSchema,
    AzureDevOpsCreatePRThreadRequestSchema,
    AzureDevOpsCreatePRThreadResponseSchema,
    AzureDevOpsCreatePRCommentRequestSchema,
    AzureDevOpsCreatePRCommentResponseSchema,
)
from ai_review.clients.azure_devops.pr.types import AzureDevOpsPullRequestsHTTPClientProtocol
from ai_review.clients.azure_devops.schema import AzureDevOpsBaseQuerySchema
from ai_review.clients.azure_devops.tools import azure_devops_extract_continuation_token
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import handle_http_error, HTTPClientError
from ai_review.libs.http.paginate import paginate_with_token


class AzureDevOpsPullRequestsHTTPClientError(HTTPClientError):
    pass


class AzureDevOpsPullRequestsHTTPClient(HTTPClient, AzureDevOpsPullRequestsHTTPClientProtocol):
    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def get_pull_request_api(
            self, organization: str, project: str, repository_id: str, pull_request_id: int
    ) -> Response:
        url = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}"
        base_query = AzureDevOpsBaseQuerySchema(api_version=settings.vcs.http_client.api_version)
        return await self.get(url=url, query=QueryParams(**base_query.model_dump(by_alias=True, exclude_none=True)))

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def get_threads_api(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            query: AzureDevOpsGetPRThreadsQuerySchema,
    ) -> Response:
        url = (
            f"/{organization}/{project}/_apis/git/repositories/"
            f"{repository_id}/pullRequests/{pull_request_id}/threads"
        )
        base_query = AzureDevOpsBaseQuerySchema(api_version=settings.vcs.http_client.api_version)
        return await self.get(
            url=url,
            query=QueryParams(
                **query.model_dump(by_alias=True, exclude_none=True),
                **base_query.model_dump(by_alias=True, exclude_none=True),
            ),
        )

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def create_thread_api(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            request: AzureDevOpsCreatePRThreadRequestSchema,
    ) -> Response:
        url = (
            f"/{organization}/{project}/_apis/git/repositories/"
            f"{repository_id}/pullRequests/{pull_request_id}/threads"
        )
        base_query = AzureDevOpsBaseQuerySchema(api_version=settings.vcs.http_client.api_version)
        return await self.post(
            url=url,
            json=request.model_dump(by_alias=True, exclude_none=True),
            query=QueryParams(**base_query.model_dump(by_alias=True, exclude_none=True)),
        )

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def create_comment_api(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            thread_id: int,
            request: AzureDevOpsCreatePRCommentRequestSchema,
    ) -> Response:
        url = (
            f"/{organization}/{project}/_apis/git/repositories/"
            f"{repository_id}/pullRequests/{pull_request_id}/threads/{thread_id}/comments"
        )
        base_query = AzureDevOpsBaseQuerySchema(api_version=settings.vcs.http_client.api_version)
        return await self.post(
            url=url,
            json=request.model_dump(by_alias=True, exclude_none=True),
            query=QueryParams(**base_query.model_dump(by_alias=True, exclude_none=True)),
        )

    @handle_http_error(client="AzureDevOpsPullRequestsHTTPClient", exception=AzureDevOpsPullRequestsHTTPClientError)
    async def get_files_api(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            iteration_id: int,
            query: AzureDevOpsGetPRFilesQuerySchema,
    ) -> Response:
        url = (
            f"/{organization}/{project}/_apis/git/repositories/"
            f"{repository_id}/pullRequests/{pull_request_id}/iterations/{iteration_id}/changes"
        )
        base_query = AzureDevOpsBaseQuerySchema(api_version=settings.vcs.http_client.api_version)
        return await self.get(
            url=url,
            query=QueryParams(
                **query.model_dump(by_alias=True, exclude_none=True),
                **base_query.model_dump(by_alias=True, exclude_none=True),
            ),
        )

    async def get_pull_request(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int
    ) -> AzureDevOpsGetPRResponseSchema:
        response = await self.get_pull_request_api(organization, project, repository_id, pull_request_id)
        return AzureDevOpsGetPRResponseSchema.model_validate_json(response.text)

    async def get_threads(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int
    ) -> AzureDevOpsGetPRThreadsResponseSchema:
        async def fetch_page(token: str | None) -> Response:
            query = AzureDevOpsGetPRThreadsQuerySchema(
                top=settings.vcs.pagination.per_page,
                continuation_token=[token] if token else None
            )
            return await self.get_threads_api(organization, project, repository_id, pull_request_id, query)

        def extract_items(response: Response) -> list[AzureDevOpsPRThreadSchema]:
            parsed = AzureDevOpsGetPRThreadsResponseSchema.model_validate_json(response.text)
            return parsed.value

        items = await paginate_with_token(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            extract_token=azure_devops_extract_continuation_token,
        )
        return AzureDevOpsGetPRThreadsResponseSchema(value=items)

    async def get_files(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            iteration_id: int
    ) -> AzureDevOpsGetPRFilesResponseSchema:
        async def fetch_page(token: str | None) -> Response:
            query = AzureDevOpsGetPRFilesQuerySchema(
                top=settings.vcs.pagination.per_page,
                continuation_token=[token] if token else None
            )
            return await self.get_files_api(organization, project, repository_id, pull_request_id, iteration_id, query)

        def extract_items(response: Response) -> list[AzureDevOpsPRChangeSchema]:
            parsed = AzureDevOpsGetPRFilesResponseSchema.model_validate_json(response.text)
            return parsed.change_entries

        items = await paginate_with_token(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            extract_token=azure_devops_extract_continuation_token,
        )
        return AzureDevOpsGetPRFilesResponseSchema(change_entries=items)

    async def create_thread(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            request: AzureDevOpsCreatePRThreadRequestSchema,
    ) -> AzureDevOpsCreatePRThreadResponseSchema:
        response = await self.create_thread_api(organization, project, repository_id, pull_request_id, request)
        return AzureDevOpsCreatePRThreadResponseSchema.model_validate_json(response.text)

    async def create_comment(
            self,
            organization: str,
            project: str,
            repository_id: str,
            pull_request_id: int,
            thread_id: int,
            request: AzureDevOpsCreatePRCommentRequestSchema,
    ) -> AzureDevOpsCreatePRCommentResponseSchema:
        response = await self.create_comment_api(
            organization, project, repository_id, pull_request_id, thread_id, request
        )
        return AzureDevOpsCreatePRCommentResponseSchema.model_validate_json(response.text)
