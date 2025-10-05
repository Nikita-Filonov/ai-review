from httpx import Response, QueryParams

from ai_review.clients.bitbucket.pr.schema.comments import (
    BitbucketPRCommentSchema,
    BitbucketGetPRCommentsQuerySchema,
    BitbucketGetPRCommentsResponseSchema,
    BitbucketCreatePRCommentRequestSchema,
    BitbucketCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket.pr.schema.files import (
    BitbucketPRFileSchema,
    BitbucketGetPRFilesQuerySchema,
    BitbucketGetPRFilesResponseSchema,
)
from ai_review.clients.bitbucket.pr.schema.pull_request import BitbucketGetPRResponseSchema
from ai_review.clients.bitbucket.pr.types import BitbucketPullRequestsHTTPClientProtocol
from ai_review.clients.bitbucket.tools import bitbucket_has_next_page
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import handle_http_error, HTTPClientError
from ai_review.libs.http.paginate import paginate


class BitbucketPullRequestsHTTPClientError(HTTPClientError):
    pass


class BitbucketPullRequestsHTTPClient(HTTPClient, BitbucketPullRequestsHTTPClientProtocol):
    @handle_http_error(client="BitbucketPullRequestsHTTPClient", exception=BitbucketPullRequestsHTTPClientError)
    async def get_pull_request_api(self, workspace: str, repo_slug: str, pull_request_id: str) -> Response:
        return await self.get(f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}")

    @handle_http_error(client="BitbucketPullRequestsHTTPClient", exception=BitbucketPullRequestsHTTPClientError)
    async def get_diffstat_api(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            query: BitbucketGetPRFilesQuerySchema,
    ) -> Response:
        return await self.get(
            f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diffstat",
            query=QueryParams(**query.model_dump(by_alias=True)),
        )

    @handle_http_error(client="BitbucketPullRequestsHTTPClient", exception=BitbucketPullRequestsHTTPClientError)
    async def get_comments_api(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            query: BitbucketGetPRCommentsQuerySchema,
    ) -> Response:
        return await self.get(
            f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments",
            query=QueryParams(**query.model_dump(by_alias=True)),
        )

    @handle_http_error(client="BitbucketPullRequestsHTTPClient", exception=BitbucketPullRequestsHTTPClientError)
    async def create_comment_api(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCreatePRCommentRequestSchema,
    ) -> Response:
        return await self.post(
            f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments",
            json=request.model_dump(by_alias=True),
        )

    async def get_pull_request(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRResponseSchema:
        resp = await self.get_pull_request_api(workspace, repo_slug, pull_request_id)
        return BitbucketGetPRResponseSchema.model_validate_json(resp.text)

    async def get_files(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRFilesResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = BitbucketGetPRFilesQuerySchema(page=page, page_len=settings.vcs.pagination.per_page)
            return await self.get_diffstat_api(workspace, repo_slug, pull_request_id, query)

        def extract_items(response: Response) -> list[BitbucketPRFileSchema]:
            result = BitbucketGetPRFilesResponseSchema.model_validate_json(response.text)
            return result.values

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=bitbucket_has_next_page
        )
        return BitbucketGetPRFilesResponseSchema(
            size=len(items),
            values=items,
            page_len=settings.vcs.pagination.per_page
        )

    async def get_comments(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRCommentsResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = BitbucketGetPRCommentsQuerySchema(page=page, page_len=settings.vcs.pagination.per_page)
            return await self.get_comments_api(workspace, repo_slug, pull_request_id, query)

        def extract_items(response: Response) -> list[BitbucketPRCommentSchema]:
            result = BitbucketGetPRCommentsResponseSchema.model_validate_json(response.text)
            return result.values

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=bitbucket_has_next_page
        )
        return BitbucketGetPRCommentsResponseSchema(
            size=len(items),
            values=items,
            page_len=settings.vcs.pagination.per_page
        )

    async def create_comment(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCreatePRCommentRequestSchema
    ) -> BitbucketCreatePRCommentResponseSchema:
        response = await self.create_comment_api(workspace, repo_slug, pull_request_id, request)
        return BitbucketCreatePRCommentResponseSchema.model_validate_json(response.text)
