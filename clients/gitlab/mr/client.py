from httpx import Response, AsyncHTTPTransport, AsyncClient

from clients.gitlab.mr.schema.changes import GitLabGetMRChangesResponseSchema
from clients.gitlab.mr.schema.comments import (
    GitLabCreateMRCommentRequestSchema,
    GitLabCreateMRCommentResponseSchema
)
from clients.gitlab.mr.schema.discussions import (
    GitLabCreateMRDiscussionRequestSchema,
    GitLabCreateMRDiscussionResponseSchema
)
from config import settings
from libs.http.client import HTTPClient
from libs.http.event_hooks.logger import LoggerEventHook
from libs.http.transports.retry import RetryTransport
from libs.logger import get_logger


class GitLabMergeRequestsHTTPClient(HTTPClient):

    async def get_mr_changes_api(self, project_id: str, merge_request_iid: str) -> Response:
        return await self.get(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_iid}/changes"
        )

    async def create_mr_comment_api(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRCommentRequestSchema,
    ) -> Response:
        return await self.post(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes",
            json=request.model_dump(),
        )

    async def create_mr_discussion_api(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRDiscussionRequestSchema,
    ) -> Response:
        return await self.post(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/discussions",
            json=request.model_dump(),
        )

    async def get_mr_changes(self, project_id: str, merge_request_id: str) -> GitLabGetMRChangesResponseSchema:
        response = await self.get_mr_changes_api(project_id, merge_request_id)
        return GitLabGetMRChangesResponseSchema.model_validate_json(response.text)

    async def create_mr_comment(
            self,
            comment: str,
            project_id: str,
            merge_request_id: str,
    ) -> GitLabCreateMRCommentResponseSchema:
        request = GitLabCreateMRCommentRequestSchema(body=comment)
        response = await self.create_mr_comment_api(
            request=request,
            project_id=project_id,
            merge_request_id=merge_request_id
        )
        return GitLabCreateMRCommentResponseSchema.model_validate_json(response.text)

    async def create_mr_discussion(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRDiscussionRequestSchema
    ):
        response = await self.create_mr_discussion_api(
            request=request,
            project_id=project_id,
            merge_request_id=merge_request_id
        )
        return GitLabCreateMRDiscussionResponseSchema.model_validate_json(response.text)


def get_gitlab_merge_requests_http_client() -> GitLabMergeRequestsHTTPClient:
    logger = get_logger("GITLAB_MERGE_REQUESTS_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(transport=AsyncHTTPTransport())

    client = AsyncClient(
        headers={"Authorization": f"Bearer {settings.gitlab.api_token}"},
        base_url=str(settings.gitlab.api_url),
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return GitLabMergeRequestsHTTPClient(client=client)
