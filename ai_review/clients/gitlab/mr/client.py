from httpx import Response

from ai_review.clients.gitlab.mr.schema.changes import GitLabGetMRChangesResponseSchema
from ai_review.clients.gitlab.mr.schema.comments import (
    GitLabGetMRCommentsResponseSchema,
    GitLabCreateMRCommentRequestSchema,
    GitLabCreateMRCommentResponseSchema,
)
from ai_review.clients.gitlab.mr.schema.discussions import (
    GitLabGetMRDiscussionsResponseSchema,
    GitLabCreateMRDiscussionRequestSchema,
    GitLabCreateMRDiscussionResponseSchema
)
from ai_review.libs.http.client import HTTPClient


class GitLabMergeRequestsHTTPClient(HTTPClient):

    async def get_changes_api(self, project_id: str, merge_request_id: str) -> Response:
        return await self.get(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/changes"
        )

    async def get_comments_api(self, project_id: str, merge_request_id: str) -> Response:
        return await self.get(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes"
        )

    async def get_discussions_api(self, project_id: str, merge_request_id: str) -> Response:
        return await self.get(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/discussions"
        )

    async def create_comment_api(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRCommentRequestSchema,
    ) -> Response:
        return await self.post(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes",
            json=request.model_dump(),
        )

    async def create_discussion_api(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRDiscussionRequestSchema,
    ) -> Response:
        return await self.post(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/discussions",
            json=request.model_dump(),
        )

    async def get_changes(self, project_id: str, merge_request_id: str) -> GitLabGetMRChangesResponseSchema:
        response = await self.get_changes_api(project_id, merge_request_id)
        return GitLabGetMRChangesResponseSchema.model_validate_json(response.text)

    async def get_comments(
            self,
            project_id: str,
            merge_request_id: str
    ) -> GitLabGetMRCommentsResponseSchema:
        response = await self.get_comments_api(project_id, merge_request_id)
        return GitLabGetMRCommentsResponseSchema.model_validate_json(response.text)

    async def get_discussions(
            self,
            project_id: str,
            merge_request_id: str
    ) -> GitLabGetMRDiscussionsResponseSchema:
        response = await self.get_discussions_api(project_id, merge_request_id)
        return GitLabGetMRDiscussionsResponseSchema.model_validate_json(response.text)

    async def create_comment(
            self,
            comment: str,
            project_id: str,
            merge_request_id: str,
    ) -> GitLabCreateMRCommentResponseSchema:
        request = GitLabCreateMRCommentRequestSchema(body=comment)
        response = await self.create_comment_api(
            request=request,
            project_id=project_id,
            merge_request_id=merge_request_id
        )
        return GitLabCreateMRCommentResponseSchema.model_validate_json(response.text)

    async def create_discussion(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRDiscussionRequestSchema
    ):
        response = await self.create_discussion_api(
            request=request,
            project_id=project_id,
            merge_request_id=merge_request_id
        )
        return GitLabCreateMRDiscussionResponseSchema.model_validate_json(response.text)
