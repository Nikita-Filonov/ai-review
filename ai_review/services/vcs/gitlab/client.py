import asyncio

from ai_review.clients.gitlab.client import get_gitlab_http_client
from ai_review.clients.gitlab.mr.schema.discussions import GitLabCreateMRDiscussionRequestSchema
from ai_review.clients.gitlab.mr.schema.draft_notes import GitLabCreateMRDraftNoteRequestSchema
from ai_review.config import settings
from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.gitlab.adapter import get_user_from_gitlab_user, get_review_comment_from_gitlab_note
from ai_review.services.vcs.gitlab.position import build_inline_position
from ai_review.services.vcs.gitlab.tools import filter_ai_review_drafts
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
        self.pending_comments = 0
        self.discarded_stale_drafts = False
        self.discard_stale_drafts_lock = asyncio.Lock()

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
        if settings.vcs.batch_comments:
            await self.create_draft_general_comment(message)
            return

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

    async def discard_stale_draft_comments(self) -> None:
        """Delete draft notes left behind by an earlier run or a concurrent job, once per process.

        GitLab's bulk publish endpoint takes no draft-note selector: it publishes every
        draft note the token user has on the merge request, regardless of which run staged
        it. Leftover drafts would therefore be posted retroactively, with diff refs that no
        longer resolve. GitLab scopes the draft-note endpoints to
        ``authored_by(current_user)``. Filter those notes by the configured ai-review tags
        so a personal or shared token cannot cause unrelated drafts to be discarded.
        """
        # Guards against a future await landing between the flag check and the flag set below; today there is none.
        async with self.discard_stale_drafts_lock:
            if self.discarded_stale_drafts:
                return

            self.discarded_stale_drafts = True

            try:
                response = await self.http_client.mr.get_draft_notes(
                    project_id=self.project_id,
                    merge_request_id=self.merge_request_id,
                )
            except Exception as error:
                logger.exception(
                    f"Failed to look up stale draft comments in {self.merge_request_ref}: {error}. "
                    f"Publishing may post leftovers from an earlier run"
                )
                return

            stale_drafts = filter_ai_review_drafts(response.root)
            preserved_count = len(response.root) - len(stale_drafts)

            if not stale_drafts:
                logger.debug(
                    f"No stale ai-review draft comments in {self.merge_request_ref}; "
                    f"preserving {preserved_count} unrelated drafts"
                )
                return

            logger.debug(
                f"Discarding stale ai-review draft notes in {self.merge_request_ref}: "
                f"{[(draft_note.id, draft_note.note) for draft_note in stale_drafts]}"
            )
            logger.warning(
                f"Discarding {len(stale_drafts)} pending ai-review draft comments from a "
                f"previous run or a concurrent job in {self.merge_request_ref}; preserving "
                f"{preserved_count} unrelated drafts"
            )
            results = await bounded_gather([
                self.http_client.mr.delete_draft_note(
                    project_id=self.project_id,
                    merge_request_id=self.merge_request_id,
                    draft_note_id=str(draft_note.id),
                )
                for draft_note in stale_drafts
            ])

            failures = [result for result in results if isinstance(result, Exception)]
            if failures:
                logger.error(
                    f"Failed to discard {len(failures)}/{len(stale_drafts)} stale draft comments "
                    f"in {self.merge_request_ref}"
                )

    async def create_draft_general_comment(self, message: str) -> None:
        await self.discard_stale_draft_comments()

        try:
            logger.info(f"Adding draft general comment to {self.merge_request_ref}: {message}")
            request = GitLabCreateMRDraftNoteRequestSchema(note=message)
            await self.http_client.mr.create_draft_note(
                request=request,
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            self.pending_comments += 1
            logger.info(f"Created draft general comment in {self.merge_request_ref}")
        except Exception as error:
            logger.exception(f"Failed to create draft general comment in {self.merge_request_ref}: {error}")
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        if settings.vcs.batch_comments:
            await self.create_draft_inline_comment(file=file, line=line, message=message)
            return

        try:
            logger.info(f"Posting inline comment in {self.merge_request_ref} at {file}:{line}: {message}")

            response = await self.http_client.mr.get_changes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )

            request = GitLabCreateMRDiscussionRequestSchema(
                body=message,
                position=build_inline_position(
                    file=file,
                    line=line,
                    diff_refs=response.diff_refs,
                    changes=response.changes,
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

    async def create_draft_inline_comment(self, file: str, line: int, message: str) -> None:
        await self.discard_stale_draft_comments()

        try:
            logger.info(f"Adding draft inline comment in {self.merge_request_ref} at {file}:{line}: {message}")

            response = await self.http_client.mr.get_changes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )

            request = GitLabCreateMRDraftNoteRequestSchema(
                note=message,
                position=build_inline_position(
                    file=file,
                    line=line,
                    diff_refs=response.diff_refs,
                    changes=response.changes,
                ),
            )
            await self.http_client.mr.create_draft_note(
                request=request,
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            self.pending_comments += 1
            logger.info(f"Created draft inline comment in {self.merge_request_ref} at {file}:{line}")
        except Exception as error:
            logger.exception(
                f"Failed to create draft inline comment in {self.merge_request_ref} at {file}:{line}: {error}"
            )
            raise

    async def publish_comments(self) -> None:
        if not settings.vcs.batch_comments or not self.pending_comments:
            return

        try:
            logger.info(f"Publishing {self.pending_comments} draft comments in {self.merge_request_ref}")
            await self.http_client.mr.bulk_publish_draft_notes(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
            )
            self.pending_comments = 0
            logger.info(f"Published draft comments in {self.merge_request_ref}")
        except Exception as error:
            logger.exception(
                f"Failed to publish draft comments in {self.merge_request_ref}: {error}. "
                f"GitLab may have published part of the batch; the remaining drafts stay pending "
                f"and the next run discards them"
            )
            raise

    async def delete_general_comment(self, comment_id: int | str) -> None:
        try:
            logger.info(f"Deleting general comment {comment_id=} in MR {self.merge_request_ref}")
            await self.http_client.mr.delete_note(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
                note_id=str(comment_id),
            )
            logger.info(f"Deleted general comment {comment_id=} in MR {self.merge_request_ref}")
        except Exception as error:
            logger.exception(f"Failed to delete general comment {comment_id=} in MR {self.merge_request_ref}: {error}")
            raise

    async def delete_inline_comment(self, comment_id: int | str) -> None:
        try:
            logger.info(f"Deleting inline comment {comment_id=} in MR {self.merge_request_ref}")
            await self.http_client.mr.delete_note(
                project_id=self.project_id,
                merge_request_id=self.merge_request_id,
                note_id=str(comment_id),
            )
            logger.info(f"Deleted inline comment {comment_id=} in MR {self.merge_request_ref}")
        except Exception as error:
            logger.exception(
                f"Failed to delete inline comment {comment_id=} in MR {self.merge_request_ref}: {error}"
            )
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
