from httpx import Response

from ai_review.clients.github.pr.schema.comments import (
    GitHubGetPRCommentsResponseSchema,
    GitHubCreateIssueCommentRequestSchema,
    GitHubCreateIssueCommentResponseSchema,
    GitHubCreateReviewCommentRequestSchema,
    GitHubCreateReviewCommentResponseSchema
)
from ai_review.clients.github.pr.schema.files import GitHubGetPRFilesResponseSchema
from ai_review.clients.github.pr.schema.pull_request import GitHubGetPRResponseSchema
from ai_review.clients.github.pr.schema.reviews import GitHubGetPRReviewsResponseSchema
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error


class GitHubPullRequestsHTTPClientError(HTTPClientError):
    pass


class GitHubPullRequestsHTTPClient(HTTPClient):
    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_pull_request_api(self, owner: str, repo: str, pull_number: str) -> Response:
        return await self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_files_api(self, owner: str, repo: str, pull_number: str) -> Response:
        return await self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}/files")

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_issue_comments_api(self, owner: str, repo: str, issue_number: str) -> Response:
        return await self.get(f"/repos/{owner}/{repo}/issues/{issue_number}/comments")

    @handle_http_error(client="GitHubPullRequestsHTTPClient", exception=GitHubPullRequestsHTTPClientError)
    async def get_review_comments_api(self, owner: str, repo: str, pull_number: str) -> Response:
        return await self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}/comments")

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
    async def get_reviews_api(self, owner: str, repo: str, pull_number: str) -> Response:
        return await self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews")

    async def get_pull_request(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRResponseSchema:
        response = await self.get_pull_request_api(owner, repo, pull_number)
        return GitHubGetPRResponseSchema.model_validate_json(response.text)

    async def get_files(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRFilesResponseSchema:
        response = await self.get_files_api(owner, repo, pull_number)
        return GitHubGetPRFilesResponseSchema.model_validate_json(response.text)

    async def get_issue_comments(self, owner: str, repo: str, issue_number: str) -> GitHubGetPRCommentsResponseSchema:
        response = await self.get_issue_comments_api(owner, repo, issue_number)
        return GitHubGetPRCommentsResponseSchema.model_validate_json(response.text)

    async def get_review_comments(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRCommentsResponseSchema:
        response = await self.get_review_comments_api(owner, repo, pull_number)
        return GitHubGetPRCommentsResponseSchema.model_validate_json(response.text)

    async def get_reviews(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRReviewsResponseSchema:
        response = await self.get_reviews_api(owner, repo, pull_number)
        return GitHubGetPRReviewsResponseSchema.model_validate_json(response.text)

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
