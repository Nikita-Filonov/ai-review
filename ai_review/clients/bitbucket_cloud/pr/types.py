from typing import Protocol

from ai_review.clients.bitbucket_cloud.pr.schema.comments import (
    BitbucketCloudGetPRCommentsResponseSchema,
    BitbucketCloudCreatePRCommentRequestSchema,
    BitbucketCloudCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket_cloud.pr.schema.files import BitbucketCloudGetPRFilesResponseSchema
from ai_review.clients.bitbucket_cloud.pr.schema.pull_request import BitbucketCloudGetPRResponseSchema


class BitbucketCloudPullRequestsHTTPClientProtocol(Protocol):
    async def get_pull_request(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRResponseSchema:
        ...

    async def get_files(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRFilesResponseSchema:
        ...

    async def get_comments(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRCommentsResponseSchema:
        ...

    async def create_comment(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCloudCreatePRCommentRequestSchema,
    ) -> BitbucketCloudCreatePRCommentResponseSchema:
        ...
