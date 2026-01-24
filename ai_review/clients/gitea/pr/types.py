from typing import Protocol

from ai_review.clients.gitea.pr.schema.comments import (
    GiteaCreateCommentRequestSchema,
    GiteaCreateCommentResponseSchema,
    GiteaGetPRCommentsResponseSchema
)
from ai_review.clients.gitea.pr.schema.files import GiteaGetPRFilesResponseSchema
from ai_review.clients.gitea.pr.schema.pull_request import GiteaGetPRResponseSchema
from ai_review.clients.gitea.pr.schema.reviews import (
    GiteaCreateReviewRequestSchema,
    GiteaCreateReviewResponseSchema
)


class GiteaPullRequestsHTTPClientProtocol(Protocol):
    async def get_pull_request(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRResponseSchema: ...

    async def get_files(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRFilesResponseSchema: ...

    async def get_comments(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRCommentsResponseSchema: ...

    async def create_comment(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GiteaCreateCommentRequestSchema
    ) -> GiteaCreateCommentResponseSchema: ...

    async def create_review(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GiteaCreateReviewRequestSchema
    ) -> GiteaCreateReviewResponseSchema: ...

    async def delete_issue_comment(self, owner: str, repo: str, comment_id: int | str) -> None: ...

    async def delete_review_comment(self, owner: str, repo: str, comment_id: int | str) -> None: ...
