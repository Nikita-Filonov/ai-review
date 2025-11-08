from httpx import Response, QueryParams

from ai_review.clients.bitbucket_server.pr.schema.changes import (
    BitbucketServerChangeSchema,
    BitbucketServerGetPRChangesQuerySchema,
    BitbucketServerGetPRChangesResponseSchema,
)
from ai_review.clients.bitbucket_server.pr.schema.comments import (
    BitbucketServerCommentSchema,
    BitbucketServerGetPRCommentsQuerySchema,
    BitbucketServerGetPRCommentsResponseSchema,
    BitbucketServerCreatePRCommentRequestSchema,
    BitbucketServerCreatePRCommentResponseSchema
)
from ai_review.clients.bitbucket_server.pr.schema.pull_request import BitbucketServerGetPRResponseSchema
from ai_review.clients.bitbucket_server.pr.types import BitbucketServerPullRequestsHTTPClientProtocol
from ai_review.clients.bitbucket_server.tools import bitbucket_server_has_next_page
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import handle_http_error, HTTPClientError
from ai_review.libs.http.paginate import paginate


class BitbucketServerPullRequestsHTTPClientError(HTTPClientError):
    pass


class BitbucketServerPullRequestsHTTPClient(HTTPClient, BitbucketServerPullRequestsHTTPClientProtocol):
    @handle_http_error(
        client="BitbucketServerPullRequestsHTTPClient",
        exception=BitbucketServerPullRequestsHTTPClientError
    )
    async def get_pull_request_api(self, project_key: str, repo_slug: str, pull_request_id: int) -> Response:
        return await self.get(f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pull_request_id}")

    @handle_http_error(
        client="BitbucketServerPullRequestsHTTPClient",
        exception=BitbucketServerPullRequestsHTTPClientError
    )
    async def get_changes_api(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
            query: BitbucketServerGetPRChangesQuerySchema,
    ) -> Response:
        return await self.get(
            f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pull_request_id}/changes",
            query=QueryParams(**query.model_dump(by_alias=True)),
        )

    @handle_http_error(
        client="BitbucketServerPullRequestsHTTPClient",
        exception=BitbucketServerPullRequestsHTTPClientError
    )
    async def get_comments_api(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
            query: BitbucketServerGetPRCommentsQuerySchema,
    ) -> Response:
        return await self.get(
            f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pull_request_id}/comments",
            query=QueryParams(**query.model_dump(by_alias=True)),
        )

    @handle_http_error(
        client="BitbucketServerPullRequestsHTTPClient",
        exception=BitbucketServerPullRequestsHTTPClientError
    )
    async def create_comment_api(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
            request: BitbucketServerCreatePRCommentRequestSchema,
    ) -> Response:
        return await self.post(
            f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pull_request_id}/comments",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def get_pull_request(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
    ) -> BitbucketServerGetPRResponseSchema:
        resp = await self.get_pull_request_api(project_key, repo_slug, pull_request_id)
        return BitbucketServerGetPRResponseSchema.model_validate_json(resp.text)

    async def get_changes(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
    ) -> BitbucketServerGetPRChangesResponseSchema:
        async def fetch_page(page: int) -> Response:
            start = (page - 1) * settings.vcs.pagination.per_page
            query = BitbucketServerGetPRChangesQuerySchema(start=start, limit=settings.vcs.pagination.per_page)
            return await self.get_changes_api(project_key, repo_slug, pull_request_id, query)

        def extract_items(response: Response) -> list[BitbucketServerChangeSchema]:
            result = BitbucketServerGetPRChangesResponseSchema.model_validate_json(response.text)
            return result.values

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=bitbucket_server_has_next_page,
        )

        return BitbucketServerGetPRChangesResponseSchema(
            size=len(items),
            start=0,
            limit=settings.vcs.pagination.per_page,
            values=items,
            is_last_page=True,
            next_page_start=None,
        )

    async def get_comments(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
    ) -> BitbucketServerGetPRCommentsResponseSchema:
        async def fetch_page(page: int) -> Response:
            start = (page - 1) * settings.vcs.pagination.per_page
            query = BitbucketServerGetPRCommentsQuerySchema(start=start, limit=settings.vcs.pagination.per_page)
            return await self.get_comments_api(project_key, repo_slug, pull_request_id, query)

        def extract_items(response: Response) -> list[BitbucketServerCommentSchema]:
            result = BitbucketServerGetPRCommentsResponseSchema.model_validate_json(response.text)
            return result.values

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=bitbucket_server_has_next_page,
        )

        return BitbucketServerGetPRCommentsResponseSchema(
            size=len(items),
            start=0,
            limit=settings.vcs.pagination.per_page,
            values=items,
            is_last_page=True,
            next_page_start=None,
        )

    async def create_comment(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
            request: BitbucketServerCreatePRCommentRequestSchema
    ) -> BitbucketServerCreatePRCommentResponseSchema:
        response = await self.create_comment_api(project_key, repo_slug, pull_request_id, request)
        return BitbucketServerCreatePRCommentResponseSchema.model_validate_json(response.text)
