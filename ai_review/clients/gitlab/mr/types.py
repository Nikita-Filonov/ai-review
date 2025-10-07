from typing import Protocol

from ai_review.clients.gitlab.mr.schema.changes import GitLabGetMRChangesResponseSchema
from ai_review.clients.gitlab.mr.schema.discussions import (
    GitLabGetMRDiscussionsResponseSchema,
    GitLabCreateMRDiscussionRequestSchema,
    GitLabCreateMRDiscussionResponseSchema,
    GitLabCreateMRDiscussionReplyResponseSchema
)
from ai_review.clients.gitlab.mr.schema.notes import GitLabGetMRNotesResponseSchema, GitLabCreateMRNoteResponseSchema


class GitLabMergeRequestsHTTPClientProtocol(Protocol):
    async def get_changes(self, project_id: str, merge_request_id: str) -> GitLabGetMRChangesResponseSchema: ...

    async def get_notes(self, project_id: str, merge_request_id: str) -> GitLabGetMRNotesResponseSchema: ...

    async def create_note(
            self,
            body: str,
            project_id: str,
            merge_request_id: str,
    ) -> GitLabCreateMRNoteResponseSchema: ...

    async def get_discussions(
            self,
            project_id: str,
            merge_request_id: str
    ) -> GitLabGetMRDiscussionsResponseSchema: ...

    async def create_discussion(
            self,
            project_id: str,
            merge_request_id: str,
            request: GitLabCreateMRDiscussionRequestSchema,
    ) -> GitLabCreateMRDiscussionResponseSchema: ...

    async def create_discussion_reply(
            self,
            project_id: str,
            merge_request_id: str,
            discussion_id: str,
            body: str,
    ) -> GitLabCreateMRDiscussionReplyResponseSchema: ...
