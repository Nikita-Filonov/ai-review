from httpx import Response, QueryParams

from ai_review.clients.gitea.pr.schema.comments import (
    GiteaPRCommentSchema,
    GiteaGetPRCommentsQuerySchema,
    GiteaGetPRCommentsResponseSchema,
    GiteaCreateCommentRequestSchema,
    GiteaCreateCommentResponseSchema
)
from ai_review.clients.gitea.pr.schema.files import (
    GiteaPRFileSchema,
    GiteaGetPRFilesQuerySchema,
    GiteaGetPRFilesResponseSchema
)
from ai_review.clients.gitea.pr.schema.pull_request import GiteaGetPRResponseSchema
from ai_review.clients.gitea.pr.types import GiteaPullRequestsHTTPClientProtocol
from ai_review.clients.gitea.tools import gitea_has_next_page
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.paginate import paginate


class GiteaPullRequestsHTTPClientError(HTTPClientError):
    pass


class GiteaPullRequestsHTTPClient(HTTPClient, GiteaPullRequestsHTTPClientProtocol):
    @handle_http_error(client="GiteaPullRequestsHTTPClient", exception=GiteaPullRequestsHTTPClientError)
    async def get_pull_request_api(self, owner: str, repo: str, pull_number: str) -> Response:
        return await self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")

    @handle_http_error(client="GiteaPullRequestsHTTPClient", exception=GiteaPullRequestsHTTPClientError)
    async def get_files_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            query: GiteaGetPRFilesQuerySchema
    ) -> Response:
        return await self.get(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
            query=QueryParams(**query.model_dump())
        )

    @handle_http_error(client="GiteaPullRequestsHTTPClient", exception=GiteaPullRequestsHTTPClientError)
    async def get_comments_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            query: GiteaGetPRCommentsQuerySchema
    ) -> Response:
        return await self.get(
            f"/repos/{owner}/{repo}/issues/{pull_number}/comments",
            query=QueryParams(**query.model_dump())
        )

    @handle_http_error(client="GiteaPullRequestsHTTPClient", exception=GiteaPullRequestsHTTPClientError)
    async def create_comment_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GiteaCreateCommentRequestSchema
    ) -> Response:
        return await self.post(
            f"/repos/{owner}/{repo}/issues/{pull_number}/comments",
            json=request.model_dump(),
        )

    async def get_pull_request(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRResponseSchema:
        response = await self.get_pull_request_api(owner, repo, pull_number)
        return GiteaGetPRResponseSchema.model_validate_json(response.text)

    async def get_files(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRFilesResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GiteaGetPRFilesQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_files_api(owner, repo, pull_number, query)

        def extract_items(response: Response) -> list[GiteaPRFileSchema]:
            result = GiteaGetPRFilesResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=gitea_has_next_page
        )
        return GiteaGetPRFilesResponseSchema(root=items)

    async def get_comments(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRCommentsResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GiteaGetPRCommentsQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_comments_api(owner, repo, pull_number, query)

        def extract_items(response: Response) -> list[GiteaPRCommentSchema]:
            result = GiteaGetPRCommentsResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=gitea_has_next_page
        )
        return GiteaGetPRCommentsResponseSchema(root=items)

    async def create_comment(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GiteaCreateCommentRequestSchema
    ) -> GiteaCreateCommentResponseSchema:
        response = await self.create_comment_api(owner, repo, pull_number, request)
        return GiteaCreateCommentResponseSchema.model_validate_json(response.text)
