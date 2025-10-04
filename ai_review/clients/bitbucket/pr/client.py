from httpx import Response, QueryParams

from ai_review.clients.bitbucket.pr.schema.comments import (
    BitbucketGetPRCommentsQuerySchema,
    BitbucketGetPRCommentsResponseSchema,
    BitbucketCreatePRCommentRequestSchema,
    BitbucketCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket.pr.schema.files import (
    BitbucketGetPRFilesQuerySchema,
    BitbucketGetPRFilesResponseSchema,
)
from ai_review.clients.bitbucket.pr.schema.pull_request import BitbucketGetPRResponseSchema
from ai_review.clients.bitbucket.pr.types import BitbucketPullRequestsHTTPClientProtocol
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import handle_http_error, HTTPClientError


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
            query=QueryParams(**query.model_dump()),
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
            query=QueryParams(**query.model_dump()),
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
        query = BitbucketGetPRFilesQuerySchema(pagelen=100)
        resp = await self.get_diffstat_api(workspace, repo_slug, pull_request_id, query)
        return BitbucketGetPRFilesResponseSchema.model_validate_json(resp.text)

    async def get_comments(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRCommentsResponseSchema:
        query = BitbucketGetPRCommentsQuerySchema(pagelen=100)
        response = await self.get_comments_api(workspace, repo_slug, pull_request_id, query)
        return BitbucketGetPRCommentsResponseSchema.model_validate_json(response.text)

    async def create_comment(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCreatePRCommentRequestSchema
    ) -> BitbucketCreatePRCommentResponseSchema:
        response = await self.create_comment_api(workspace, repo_slug, pull_request_id, request)
        return BitbucketCreatePRCommentResponseSchema.model_validate_json(response.text)
