from typing import Protocol

from ai_review.clients.bitbucket_server.pr.schema.changes import BitbucketServerGetPRChangesResponseSchema
from ai_review.clients.bitbucket_server.pr.schema.comments import (
    BitbucketServerGetPRCommentsResponseSchema,
    BitbucketServerCreatePRCommentRequestSchema,
    BitbucketServerCreatePRCommentResponseSchema
)
from ai_review.clients.bitbucket_server.pr.schema.pull_request import BitbucketServerGetPRResponseSchema


class BitbucketServerPullRequestsHTTPClientProtocol(Protocol):
    async def get_pull_request(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
    ) -> BitbucketServerGetPRResponseSchema:
        ...

    async def get_changes(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
    ) -> BitbucketServerGetPRChangesResponseSchema:
        ...

    async def get_comments(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
    ) -> BitbucketServerGetPRCommentsResponseSchema:
        ...

    async def create_comment(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
            request: BitbucketServerCreatePRCommentRequestSchema,
    ) -> BitbucketServerCreatePRCommentResponseSchema:
        ...
