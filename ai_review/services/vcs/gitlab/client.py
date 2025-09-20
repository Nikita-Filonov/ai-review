from ai_review.clients.gitlab.client import get_gitlab_http_client
from ai_review.clients.gitlab.mr.schema.discussions import (
    GitLabDiscussionPositionSchema,
    GitLabCreateMRDiscussionRequestSchema
)
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.types import (
    VCSClient,
    MRUserSchema,
    MRInfoSchema,
    MRNoteSchema,
    MRCommentSchema,
    MRDiscussionSchema,
)

logger = get_logger("GITLAB_VCS_CLIENT")


class GitLabVCSClient(VCSClient):
    def __init__(self):
        self.http_client = get_gitlab_http_client()
        self.project_id = settings.vcs.pipeline.project_id
        self.merge_request_id = settings.vcs.pipeline.merge_request_id

    async def get_mr_info(self) -> MRInfoSchema:
        try:
            response = await self.http_client.mr.get_changes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Fetched MR info for project_id={self.project_id} merge_request_id={self.merge_request_id}")

            return MRInfoSchema(
                title=response.title,
                author=MRUserSchema(
                    name=response.author.name,
                    username=response.author.username
                ),
                labels=response.labels,
                base_sha=response.diff_refs.base_sha,
                head_sha=response.diff_refs.head_sha,
                start_sha=response.diff_refs.start_sha,
                reviewers=[
                    MRUserSchema(name=reviewer.name, username=reviewer.username)
                    for reviewer in response.reviewers
                ],
                assignees=[
                    MRUserSchema(name=assignee.name, username=assignee.username)
                    for assignee in response.assignees
                ],
                description=response.description,
                source_branch=response.source_branch,
                target_branch=response.target_branch,
                changed_files=[change.new_path for change in response.changes if change.new_path],
            )
        except Exception as error:
            logger.exception(
                f"Failed to fetch MR info project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}: {error}"
            )
            return MRInfoSchema()

    async def get_comments(self) -> list[MRCommentSchema]:
        try:
            response = await self.http_client.mr.get_comments(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(
                f"Fetched comments for project_id={self.project_id} merge_request_id={self.merge_request_id}"
            )

            return [MRCommentSchema(id=comment.id, body=comment.body) for comment in response.root]
        except Exception as error:
            logger.exception(
                f"Failed to fetch comments project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}: {error}"
            )
            return []

    async def get_discussions(self) -> list[MRDiscussionSchema]:
        try:
            response = await self.http_client.mr.get_discussions(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(
                f"Fetched discussions for project_id={self.project_id} merge_request_id={self.merge_request_id}"
            )

            return [
                MRDiscussionSchema(
                    id=discussion.id,
                    notes=[MRNoteSchema(id=note.id, body=note.body or "") for note in discussion.notes],
                )
                for discussion in response.root
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch discussions project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}: {error}"
            )
            return []

    async def create_comment(self, message: str) -> None:
        try:
            logger.info(
                f"Posting comment to merge_request_id={self.merge_request_id}: {message}",
            )
            await self.http_client.mr.create_comment(
                comment=message,
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Created comment in {self.merge_request_id=}")
        except Exception as error:
            logger.exception(f"Failed to create comment in merge_request_id={self.merge_request_id}: {error}")

    async def create_discussion(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(
                f"Posting discussion to merge_request_id={self.merge_request_id} at {file}:{line}: {message}"
            )

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
            logger.info(f"Created discussion in merge_request_id={self.merge_request_id} at {file}:{line}")
        except Exception as error:
            logger.exception(
                f"Failed to create discussion in merge_request_id={self.merge_request_id} "
                f"at {file}:{line}: {error}"
            )
