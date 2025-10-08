from httpx import Response, QueryParams

from ai_review.clients.github.pr.schema.comments import (
    GitHubPRCommentSchema,
    GitHubIssueCommentSchema,
    GitHubGetPRCommentsQuerySchema,
    GitHubGetPRCommentsResponseSchema,
    GitHubGetIssueCommentsResponseSchema,
    GitHubCreateIssueCommentRequestSchema,
    GitHubCreateIssueCommentResponseSchema,
    GitHubCreateReviewReplyRequestSchema,
    GitHubCreateReviewCommentRequestSchema,
    GitHubCreateReviewCommentResponseSchema
)
from ai_review.clients.github.pr.schema.files import (
    GitHubPRFileSchema,
    GitHubGetPRFilesQuerySchema,
    GitHubGetPRFilesResponseSchema
)
from ai_review.clients.github.pr.schema.pull_request import GitHubGetPRResponseSchema
from ai_review.clients.github.pr.schema.reviews import (
    GitHubPRReviewSchema,
    GitHubGetPRReviewsQuerySchema,
    GitHubGetPRReviewsResponseSchema
)
from ai_review.clients.github.pr.types import GitHubPullRequestsHTTPClientProtocol
from ai_review.clients.github.tools import github_has_next_page
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.paginate import paginate


class GitHubPullRequestsHTTPClientError(HTTPClientError):
    pass


class GitHubPullRequestsHTTPClient(HTTPClient, GitHubPullRequestsHTTPClientProtocol):
    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_pull_request_api(self, owner: str, repo: str, pull_number: str) -> Response:
        return await self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_files_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            query: GitHubGetPRFilesQuerySchema
    ) -> Response:
        return await self.get(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
            query=QueryParams(**query.model_dump())
        )

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_issue_comments_api(
            self,
            owner: str,
            repo: str,
            issue_number: str,
            query: GitHubGetPRCommentsQuerySchema,
    ) -> Response:
        return await self.get(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            query=QueryParams(**query.model_dump())
        )

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_review_comments_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            query: GitHubGetPRCommentsQuerySchema,
    ) -> Response:
        return await self.get(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/comments",
            query=QueryParams(**query.model_dump())
        )

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def create_review_reply_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GitHubCreateReviewReplyRequestSchema,
    ) -> Response:
        return await self.post(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/comments",
            json=request.model_dump(),
        )

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def create_review_comment_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GitHubCreateReviewCommentRequestSchema,
    ) -> Response:
        return await self.post(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/comments",
            json=request.model_dump(),
        )

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def create_issue_comment_api(
            self,
            owner: str,
            repo: str,
            issue_number: str,
            request: GitHubCreateIssueCommentRequestSchema,
    ) -> Response:
        return await self.post(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json=request.model_dump(),
        )

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_reviews_api(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            query: GitHubGetPRReviewsQuerySchema
    ) -> Response:
        return await self.get(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
            query=QueryParams(**query.model_dump())
        )

    async def get_pull_request(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRResponseSchema:
        response = await self.get_pull_request_api(owner, repo, pull_number)
        return GitHubGetPRResponseSchema.model_validate_json(response.text)

    async def get_files(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRFilesResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GitHubGetPRFilesQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_files_api(owner, repo, pull_number, query)

        def extract_items(response: Response) -> list[GitHubPRFileSchema]:
            result = GitHubGetPRFilesResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=github_has_next_page
        )
        return GitHubGetPRFilesResponseSchema(root=items)

    async def get_issue_comments(
            self,
            owner: str,
            repo: str,
            issue_number: str
    ) -> GitHubGetIssueCommentsResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GitHubGetPRCommentsQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_issue_comments_api(owner, repo, issue_number, query)

        def extract_items(response: Response) -> list[GitHubIssueCommentSchema]:
            result = GitHubGetIssueCommentsResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=github_has_next_page
        )
        return GitHubGetIssueCommentsResponseSchema(root=items)

    async def get_review_comments(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRCommentsResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GitHubGetPRCommentsQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_review_comments_api(owner, repo, pull_number, query)

        def extract_items(response: Response) -> list[GitHubPRCommentSchema]:
            result = GitHubGetPRCommentsResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=github_has_next_page
        )
        return GitHubGetPRCommentsResponseSchema(root=items)

    async def get_reviews(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRReviewsResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GitHubGetPRReviewsQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_reviews_api(owner, repo, pull_number, query)

        def extract_items(response: Response) -> list[GitHubPRReviewSchema]:
            result = GitHubGetPRReviewsResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=github_has_next_page
        )
        return GitHubGetPRReviewsResponseSchema(root=items)

    async def create_review_reply(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GitHubCreateReviewReplyRequestSchema,
    ) -> GitHubCreateReviewCommentResponseSchema:
        response = await self.create_review_reply_api(owner, repo, pull_number, request)
        return GitHubCreateReviewCommentResponseSchema.model_validate_json(response.text)

    async def create_review_comment(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GitHubCreateReviewCommentRequestSchema
    ) -> GitHubCreateReviewCommentResponseSchema:
        response = await self.create_review_comment_api(owner, repo, pull_number, request)
        return GitHubCreateReviewCommentResponseSchema.model_validate_json(response.text)

    async def create_issue_comment(
            self,
            owner: str,
            repo: str,
            issue_number: str,
            body: str,
    ) -> GitHubCreateIssueCommentResponseSchema:
        request = GitHubCreateIssueCommentRequestSchema(body=body)
        response = await self.create_issue_comment_api(owner, repo, issue_number, request)
        return GitHubCreateIssueCommentResponseSchema.model_validate_json(response.text)
