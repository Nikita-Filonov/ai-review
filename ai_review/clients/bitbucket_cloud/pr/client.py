from httpx import Response, QueryParams

from ai_review.clients.bitbucket_cloud.pr.schema.comments import (
    BitbucketCloudPRCommentSchema,
    BitbucketCloudGetPRCommentsQuerySchema,
    BitbucketCloudGetPRCommentsResponseSchema,
    BitbucketCloudCreatePRCommentRequestSchema,
    BitbucketCloudCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket_cloud.pr.schema.files import (
    BitbucketCloudPRFileSchema,
    BitbucketCloudGetPRFilesQuerySchema,
    BitbucketCloudGetPRFilesResponseSchema,
)
from ai_review.clients.bitbucket_cloud.pr.schema.pull_request import BitbucketCloudGetPRResponseSchema
from ai_review.clients.bitbucket_cloud.pr.types import BitbucketCloudPullRequestsHTTPClientProtocol
from ai_review.clients.bitbucket_cloud.tools import bitbucket_cloud_has_next_page
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import handle_http_error, HTTPClientError
from ai_review.libs.http.paginate import paginate


class BitbucketCloudPullRequestsHTTPClientError(HTTPClientError):
    pass


class BitbucketCloudPullRequestsHTTPClient(HTTPClient, BitbucketCloudPullRequestsHTTPClientProtocol):
    @handle_http_error(
        client="BitbucketCloudPullRequestsHTTPClient",
        exception=BitbucketCloudPullRequestsHTTPClientError
    )
    async def get_pull_request_api(self, workspace: str, repo_slug: str, pull_request_id: str) -> Response:
        return await self.get(f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}")

    @handle_http_error(
        client="BitbucketCloudPullRequestsHTTPClient",
        exception=BitbucketCloudPullRequestsHTTPClientError
    )
    async def get_diffstat_api(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            query: BitbucketCloudGetPRFilesQuerySchema,
    ) -> Response:
        return await self.get(
            f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diffstat",
            query=QueryParams(**query.model_dump(by_alias=True)),
        )

    @handle_http_error(
        client="BitbucketCloudPullRequestsHTTPClient",
        exception=BitbucketCloudPullRequestsHTTPClientError
    )
    async def get_comments_api(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            query: BitbucketCloudGetPRCommentsQuerySchema,
    ) -> Response:
        return await self.get(
            f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments",
            query=QueryParams(**query.model_dump(by_alias=True)),
        )

    @handle_http_error(
        client="BitbucketCloudPullRequestsHTTPClient",
        exception=BitbucketCloudPullRequestsHTTPClientError
    )
    async def create_comment_api(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCloudCreatePRCommentRequestSchema,
    ) -> Response:
        return await self.post(
            f"/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def get_pull_request(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRResponseSchema:
        resp = await self.get_pull_request_api(workspace, repo_slug, pull_request_id)
        return BitbucketCloudGetPRResponseSchema.model_validate_json(resp.text)

    async def get_files(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRFilesResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = BitbucketCloudGetPRFilesQuerySchema(page=page, page_len=settings.vcs.pagination.per_page)
            return await self.get_diffstat_api(workspace, repo_slug, pull_request_id, query)

        def extract_items(response: Response) -> list[BitbucketCloudPRFileSchema]:
            result = BitbucketCloudGetPRFilesResponseSchema.model_validate_json(response.text)
            return result.values

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=bitbucket_cloud_has_next_page
        )
        return BitbucketCloudGetPRFilesResponseSchema(
            size=len(items),
            values=items,
            page_len=settings.vcs.pagination.per_page
        )

    async def get_comments(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRCommentsResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = BitbucketCloudGetPRCommentsQuerySchema(page=page, page_len=settings.vcs.pagination.per_page)
            return await self.get_comments_api(workspace, repo_slug, pull_request_id, query)

        def extract_items(response: Response) -> list[BitbucketCloudPRCommentSchema]:
            result = BitbucketCloudGetPRCommentsResponseSchema.model_validate_json(response.text)
            return result.values

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=bitbucket_cloud_has_next_page
        )
        return BitbucketCloudGetPRCommentsResponseSchema(
            size=len(items),
            values=items,
            page_len=settings.vcs.pagination.per_page
        )

    async def create_comment(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCloudCreatePRCommentRequestSchema
    ) -> BitbucketCloudCreatePRCommentResponseSchema:
        response = await self.create_comment_api(workspace, repo_slug, pull_request_id, request)
        return BitbucketCloudCreatePRCommentResponseSchema.model_validate_json(response.text)
