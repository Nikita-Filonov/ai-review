from typing import Protocol

from ai_review.clients.github.pr.schema.comments import (
    GitHubGetPRCommentsResponseSchema,
    GitHubGetIssueCommentsResponseSchema,
    GitHubCreateIssueCommentResponseSchema,
    GitHubCreateReviewReplyRequestSchema,
    GitHubCreateReviewCommentResponseSchema,
    GitHubCreateReviewCommentRequestSchema,
)
from ai_review.clients.github.pr.schema.files import GitHubGetPRFilesResponseSchema
from ai_review.clients.github.pr.schema.pull_request import GitHubGetPRResponseSchema


class GitHubPullRequestsHTTPClientProtocol(Protocol):
    async def get_pull_request(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRResponseSchema: ...

    async def get_files(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRFilesResponseSchema: ...

    async def get_issue_comments(
            self,
            owner: str,
            repo: str,
            issue_number: str
    ) -> GitHubGetIssueCommentsResponseSchema: ...

    async def get_review_comments(
            self,
            owner: str,
            repo: str,
            pull_number: str
    ) -> GitHubGetPRCommentsResponseSchema: ...

    async def create_review_reply(
            self,
            owner: str,
            repo: str,
            comment_id: str,
            request: GitHubCreateReviewReplyRequestSchema,
    ) -> GitHubCreateReviewCommentResponseSchema: ...

    async def create_review_comment(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GitHubCreateReviewCommentRequestSchema,
    ) -> GitHubCreateReviewCommentResponseSchema: ...

    async def create_issue_comment(
            self,
            owner: str,
            repo: str,
            issue_number: str,
            body: str,
    ) -> GitHubCreateIssueCommentResponseSchema: ...
