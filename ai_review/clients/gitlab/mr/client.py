from httpx import Response, QueryParams

from ai_review.clients.gitlab.mr.schema.changes import GitLabGetMRChangesResponseSchema
from ai_review.clients.gitlab.mr.schema.discussions import (
    GitLabDiscussionSchema,
    GitLabGetMRDiscussionsQuerySchema,
    GitLabGetMRDiscussionsResponseSchema,
    GitLabCreateMRDiscussionRequestSchema,
    GitLabCreateMRDiscussionResponseSchema,
    GitLabCreateMRDiscussionReplyRequestSchema,
    GitLabCreateMRDiscussionReplyResponseSchema
)
from ai_review.clients.gitlab.mr.schema.notes import (
    GitLabNoteSchema,
    GitLabGetMRNotesQuerySchema,
    GitLabGetMRNotesResponseSchema,
    GitLabCreateMRNoteRequestSchema,
    GitLabCreateMRNoteResponseSchema,
)
from ai_review.clients.gitlab.mr.types import GitLabMergeRequestsHTTPClientProtocol
from ai_review.clients.gitlab.tools import gitlab_has_next_page
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.handlers import handle_http_error, HTTPClientError
from ai_review.libs.http.paginate import paginate


class GitLabMergeRequestsHTTPClientError(HTTPClientError):
    pass


class GitLabMergeRequestsHTTPClient(HTTPClient, GitLabMergeRequestsHTTPClientProtocol):
    @handle_http_error(client="GitLabMergeRequestsHTTPClient", exception=GitLabMergeRequestsHTTPClientError)
    async def get_changes_api(self, project_id: str, merge_request_id: str) -> Response:
        return await self.get(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/changes"
        )

    @handle_http_error(client="GitLabMergeRequestsHTTPClient", exception=GitLabMergeRequestsHTTPClientError)
    async def get_notes_api(
            self,
            project_id: str,
            merge_request_id: str,
            query: GitLabGetMRNotesQuerySchema
    ) -> Response:
        return await self.get(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes",
            query=QueryParams(**query.model_dump())
        )

    @handle_http_error(client="GitLabMergeRequestsHTTPClient", exception=GitLabMergeRequestsHTTPClientError)
    async def get_discussions_api(
            self,
            project_id: str,
            merge_request_id: str,
            query: GitLabGetMRDiscussionsQuerySchema
    ) -> Response:
        return await self.get(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/discussions",
            query=QueryParams(**query.model_dump())
        )

    @handle_http_error(client="GitLabMergeRequestsHTTPClient", exception=GitLabMergeRequestsHTTPClientError)
    async def create_note_api(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRNoteRequestSchema,
    ) -> Response:
        return await self.post(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes",
            json=request.model_dump(),
        )

    @handle_http_error(client="GitLabMergeRequestsHTTPClient", exception=GitLabMergeRequestsHTTPClientError)
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

    @handle_http_error(client="GitLabMergeRequestsHTTPClient", exception=GitLabMergeRequestsHTTPClientError)
    async def create_discussion_reply_api(
            self,
            project_id: str,
            merge_request_id: str,
            discussion_id: str,
            request: GitLabCreateMRDiscussionReplyRequestSchema,
    ) -> Response:
        return await self.post(
            f"/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/discussions/{discussion_id}/notes",
            json=request.model_dump(),
        )

    async def get_changes(self, project_id: str, merge_request_id: str) -> GitLabGetMRChangesResponseSchema:
        response = await self.get_changes_api(project_id, merge_request_id)
        return GitLabGetMRChangesResponseSchema.model_validate_json(response.text)

    async def get_notes(
            self,
            project_id: str,
            merge_request_id: str
    ) -> GitLabGetMRNotesResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GitLabGetMRNotesQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_notes_api(project_id, merge_request_id, query)

        def extract_items(response: Response) -> list[GitLabNoteSchema]:
            result = GitLabGetMRNotesResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=gitlab_has_next_page
        )
        return GitLabGetMRNotesResponseSchema(root=items)

    async def get_discussions(
            self,
            project_id: str,
            merge_request_id: str
    ) -> GitLabGetMRDiscussionsResponseSchema:
        async def fetch_page(page: int) -> Response:
            query = GitLabGetMRDiscussionsQuerySchema(page=page, per_page=settings.vcs.pagination.per_page)
            return await self.get_discussions_api(project_id, merge_request_id, query)

        def extract_items(response: Response) -> list[GitLabDiscussionSchema]:
            result = GitLabGetMRDiscussionsResponseSchema.model_validate_json(response.text)
            return result.root

        items = await paginate(
            max_pages=settings.vcs.pagination.max_pages,
            fetch_page=fetch_page,
            extract_items=extract_items,
            has_next_page=gitlab_has_next_page
        )
        return GitLabGetMRDiscussionsResponseSchema(root=items)

    async def create_note(
            self,
            body: str,
            project_id: str,
            merge_request_id: str,
    ) -> GitLabCreateMRNoteResponseSchema:
        request = GitLabCreateMRNoteRequestSchema(body=body)
        response = await self.create_note_api(
            request=request,
            project_id=project_id,
            merge_request_id=merge_request_id
        )
        return GitLabCreateMRNoteResponseSchema.model_validate_json(response.text)

    async def create_discussion(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRDiscussionRequestSchema
    ) -> GitLabCreateMRDiscussionResponseSchema:
        response = await self.create_discussion_api(
            request=request,
            project_id=project_id,
            merge_request_id=merge_request_id
        )
        return GitLabCreateMRDiscussionResponseSchema.model_validate_json(response.text)

    async def create_discussion_reply(
            self,
            project_id: str,
            merge_request_id: str,
            discussion_id: str,
            body: str,
    ) -> GitLabCreateMRDiscussionReplyResponseSchema:
        request = GitLabCreateMRDiscussionReplyRequestSchema(body=body)
        response = await self.create_discussion_reply_api(
            project_id=project_id,
            merge_request_id=merge_request_id,
            discussion_id=discussion_id,
            request=request,
        )
        return GitLabCreateMRDiscussionReplyResponseSchema.model_validate_json(response.text)
