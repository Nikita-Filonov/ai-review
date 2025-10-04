from typing import Protocol

from ai_review.clients.bitbucket.pr.schema.comments import (
    BitbucketGetPRCommentsResponseSchema,
    BitbucketCreatePRCommentRequestSchema,
    BitbucketCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket.pr.schema.files import BitbucketGetPRFilesResponseSchema
from ai_review.clients.bitbucket.pr.schema.pull_request import BitbucketGetPRResponseSchema


class BitbucketPullRequestsHTTPClientProtocol(Protocol):
    async def get_pull_request(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRResponseSchema:
        ...

    async def get_files(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRFilesResponseSchema:
        ...

    async def get_comments(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRCommentsResponseSchema:
        ...

    async def create_comment(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCreatePRCommentRequestSchema,
    ) -> BitbucketCreatePRCommentResponseSchema:
        ...
