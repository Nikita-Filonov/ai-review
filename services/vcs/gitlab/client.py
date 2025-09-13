from clients.gitlab.client import get_gitlab_http_client
from clients.gitlab.mr.schema.discussions import (
    GitLabDiscussionPositionSchema,
    GitLabCreateMRDiscussionRequestSchema
)
from config import settings
from services.vcs.types import VCSClient, MRInfoSchema, MRDiscussionSchema, MRNoteSchema


class GitLabVCSClient(VCSClient):
    def __init__(self):
        self.http_client = get_gitlab_http_client()
        self.project_id = settings.vcs.pipeline.project_id
        self.merge_request_id = settings.vcs.pipeline.merge_request_id

    async def get_mr_info(self) -> MRInfoSchema:
        response = await self.http_client.mr.get_changes(
            project_id=self.project_id,
            merge_request_id=self.merge_request_id,
        )

        return MRInfoSchema(
            title=response.title,
            description=response.description,
            base_sha=response.diff_refs.base_sha,
            head_sha=response.diff_refs.head_sha,
            start_sha=response.diff_refs.start_sha,
            changed_files=[c.new_path for c in response.changes if c.new_path],
        )

    async def get_discussions(self) -> list[MRDiscussionSchema]:
        response = await self.http_client.mr.get_discussions(
            project_id=self.project_id,
            merge_request_id=self.merge_request_id,
        )
        return [
            MRDiscussionSchema(
                id=discussion.id,
                notes=[MRNoteSchema(id=note.id, body=note.body or "") for note in discussion.notes],
            )
            for discussion in response.root
        ]

    async def create_comment(self, message: str) -> None:
        await self.http_client.mr.create_comment(
            comment=message,
            project_id=self.project_id,
            merge_request_id=self.merge_request_id,
        )

    async def create_discussion(self, file: str, line: int, message: str) -> None:
        response = await self.http_client.mr.get_changes(
            project_id=self.project_id,
            merge_request_id=self.merge_request_id,
        )

        request = GitLabCreateMRDiscussionRequestSchema(
            body=message,
            position=GitLabDiscussionPositionSchema(
                position_type="text",
                base_sha=response.diff_refs.base_sha,
                head_sha=response.diff_refs.head_sha,
                start_sha=response.diff_refs.start_sha,
                new_path=file,
                new_line=line,
            )
        )
        await self.http_client.mr.create_discussion(
            request=request,
            project_id=self.project_id,
            merge_request_id=self.merge_request_id,
        )
