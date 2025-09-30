from ai_review.clients.gitlab.client import get_gitlab_http_client
from ai_review.clients.gitlab.mr.schema.discussions import (
    GitLabDiscussionPositionSchema,
    GitLabCreateMRDiscussionRequestSchema,
)
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    UserSchema,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewCommentSchema,
)

logger = get_logger("GITLAB_VCS_CLIENT")


class GitLabVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_gitlab_http_client()
        self.project_id = settings.vcs.pipeline.project_id
        self.merge_request_id = settings.vcs.pipeline.merge_request_id

    async def get_review_info(self) -> ReviewInfoSchema:
        try:
            response = await self.http_client.mr.get_changes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(
                f"Fetched MR info for project_id={self.project_id} merge_request_id={self.merge_request_id}"
            )

            return ReviewInfoSchema(
                id=response.iid,
                title=response.title,
                description=response.description,
                author=UserSchema(
                    name=response.author.name,
                    username=response.author.username,
                    id=response.author.id,
                ),
                labels=response.labels,
                base_sha=response.diff_refs.base_sha,
                head_sha=response.diff_refs.head_sha,
                start_sha=response.diff_refs.start_sha,
                reviewers=[
                    UserSchema(id=user.id, name=user.name, username=user.username)
                    for user in response.reviewers
                ],
                assignees=[
                    UserSchema(id=user.id, name=user.name, username=user.username)
                    for user in response.assignees
                ],
                source_branch=BranchRefSchema(
                    ref=response.source_branch,
                    sha=response.diff_refs.head_sha,
                ),
                target_branch=BranchRefSchema(
                    ref=response.target_branch,
                    sha=response.diff_refs.base_sha,
                ),
                changed_files=[
                    change.new_path for change in response.changes if change.new_path
                ],
            )
        except Exception as error:
            logger.exception(
                f"Failed to fetch MR info for project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}: {error}"
            )
            return ReviewInfoSchema()

    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.mr.get_notes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(
                f"Fetched general comments for project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}"
            )

            return [
                ReviewCommentSchema(id=note.id, body=note.body or "")
                for note in response.root
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch general comments project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}: {error}"
            )
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.mr.get_discussions(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(
                f"Fetched inline discussions for project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}"
            )

            return [
                ReviewCommentSchema(id=note.id, body=note.body or "")
                for discussion in response.root
                for note in discussion.notes
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch inline discussions project_id={self.project_id} "
                f"merge_request_id={self.merge_request_id}: {error}"
            )
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(
                f"Posting general comment to merge_request_id={self.merge_request_id}: {message}"
            )
            await self.http_client.mr.create_note(
                body=message,
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Created general comment in merge_request_id={self.merge_request_id}")
        except Exception as error:
            logger.exception(
                f"Failed to create general comment in merge_request_id={self.merge_request_id}: {error}"
            )
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(
                f"Posting inline comment in merge_request_id={self.merge_request_id} at {file}:{line}: {message}"
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
                ),
            )
            await self.http_client.mr.create_discussion(
                request=request,
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(
                f"Created inline comment in merge_request_id={self.merge_request_id} at {file}:{line}"
            )
        except Exception as error:
            logger.exception(
                f"Failed to create inline comment in merge_request_id={self.merge_request_id} "
                f"at {file}:{line}: {error}"
            )
            raise
