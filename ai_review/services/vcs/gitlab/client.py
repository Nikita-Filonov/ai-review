from ai_review.clients.gitlab.client import get_gitlab_http_client
from ai_review.clients.gitlab.mr.schema.discussions import GitLabCreateMRDiscussionRequestSchema
from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.gitlab.adapter import get_user_from_gitlab_user, get_review_comment_from_gitlab_note
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    UserSchema,
    ThreadKind,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)

logger = get_logger("GITLAB_VCS_CLIENT")


class GitLabVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_gitlab_http_client()
        self.project_id = settings.vcs.pipeline.project_id
        self.merge_request_id = settings.vcs.pipeline.merge_request_id
        self.merge_request_ref = f"project_id={self.project_id} merge_request_id={self.merge_request_id}"

    # --- Review info ---
    async def get_review_info(self) -> ReviewInfoSchema:
        try:
            response = await self.http_client.mr.get_changes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Fetched MR info for {self.merge_request_ref}")

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
            logger.exception(f"Failed to fetch MR info for {self.merge_request_ref}: {error}")
            return ReviewInfoSchema()

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.mr.get_notes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Fetched general comments for {self.merge_request_ref}")

            return [
                ReviewCommentSchema(
                    id=note.id,
                    body=note.body or "",
                    author=get_user_from_gitlab_user(note.author),
                    thread_id=note.id
                )
                for note in response.root
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch general comments {self.merge_request_ref}: {error}")
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.mr.get_discussions(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Fetched inline discussions for {self.merge_request_ref}")

            return [
                get_review_comment_from_gitlab_note(note, discussion)
                for discussion in response.root
                for note in discussion.notes
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch inline discussions {self.merge_request_ref}: {error}")
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(f"Posting general comment to {self.merge_request_ref}: {message}")
            await self.http_client.mr.create_note(
                body=message,
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Created general comment in {self.merge_request_ref}")
        except Exception as error:
            logger.exception(f"Failed to create general comment in {self.merge_request_ref}: {error}")
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(f"Posting inline comment in {self.merge_request_ref} at {file}:{line}: {message}")

            response = await self.http_client.mr.get_changes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )

            request = GitLabCreateMRDiscussionRequestSchema(
                body=message,
                position=GitLabPositionSchema(
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
            logger.info(f"Created inline comment in {self.merge_request_ref} at {file}:{line}")
        except Exception as error:
            logger.exception(f"Failed to create inline comment in {self.merge_request_ref} at {file}:{line}: {error}")
            raise

    # --- Replies ---
    async def create_inline_reply(self, thread_id: str | int, message: str) -> None:
        try:
            logger.info(f"Replying to discussion {thread_id=} in MR {self.merge_request_ref}")
            await self.http_client.mr.create_discussion_reply(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
                discussion_id=str(thread_id),
                body=message,
            )
            logger.info(
                f"Created inline reply to discussion {thread_id=} in MR {self.merge_request_ref}"
            )
        except Exception as error:
            logger.exception(
                f"Failed to create inline reply to discussion {thread_id=} in MR {self.merge_request_ref}: {error}"
            )
            raise

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        try:
            logger.info(f"Replying to general comment {thread_id=} in MR {self.merge_request_ref}")
            await self.create_general_comment(message)
        except Exception as error:
            logger.exception(
                f"Failed to reply to general comment {thread_id=} in MR {self.merge_request_ref}: {error}"
            )
            raise

    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        try:
            response = await self.http_client.mr.get_discussions(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            logger.info(f"Fetched inline threads for MR {self.merge_request_ref}")

            threads: list[ReviewThreadSchema] = []
            for discussion in response.root:
                if not discussion.notes:
                    continue

                position = discussion.position or (
                    discussion.notes[0].position if discussion.notes else None
                )

                threads.append(
                    ReviewThreadSchema(
                        id=discussion.id,
                        kind=ThreadKind.INLINE,
                        file=position.new_path if position else None,
                        line=position.new_line if position else None,
                        comments=[
                            get_review_comment_from_gitlab_note(note, discussion)
                            for note in discussion.notes
                        ],
                    )
                )

            logger.info(f"Built {len(threads)} inline threads for MR {self.merge_request_ref}")
            return threads
        except Exception as error:
            logger.exception(f"Failed to fetch inline threads for MR {self.merge_request_ref}: {error}")
            return []

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        try:
            comments = await self.get_general_comments()

            threads = [
                ReviewThreadSchema(id=comment.id, kind=ThreadKind.SUMMARY, comments=[comment])
                for comment in comments
            ]
            logger.info(f"Built {len(threads)} general threads for MR {self.merge_request_ref}")
            return threads
        except Exception as error:
            logger.exception(f"Failed to build general threads for MR {self.merge_request_ref}: {error}")
            return []
