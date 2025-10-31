from collections import defaultdict

from ai_review.clients.bitbucket_server.client import get_bitbucket_server_http_client
from ai_review.clients.bitbucket_server.pr.schema.comments import (
    BitbucketServerCommentAnchorSchema,
    BitbucketServerCommentParentSchema,
    BitbucketServerCreatePRCommentRequestSchema
)
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.bitbucket_server.adapter import get_review_comment_from_bitbucket_server_comment
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ThreadKind,
    UserSchema,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)

logger = get_logger("BITBUCKET_SERVER_VCS_CLIENT")


class BitbucketServerVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_bitbucket_server_http_client()
        self.project_key = settings.vcs.pipeline.project_key
        self.repo_slug = settings.vcs.pipeline.repo_slug
        self.pull_request_id = settings.vcs.pipeline.pull_request_id
        self.pull_request_ref = f"{self.project_key}/{self.repo_slug}#{self.pull_request_id}"

    # --- Review info ---
    async def get_review_info(self) -> ReviewInfoSchema:
        try:
            pr = await self.http_client.pr.get_pull_request(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            changes = await self.http_client.pr.get_changes(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )

            logger.info(f"Fetched PR info for {self.pull_request_ref}")

            return ReviewInfoSchema(
                id=pr.id,
                title=pr.title,
                description=pr.description or "",
                author=UserSchema(
                    id=pr.author.user.id,
                    name=pr.author.user.display_name or "",
                    username=pr.author.user.slug or pr.author.user.name,
                ),
                labels=[],
                base_sha=pr.to_ref.latest_commit,
                head_sha=pr.from_ref.latest_commit,
                assignees=[],
                reviewers=[
                    UserSchema(
                        id=user.user.id,
                        name=user.user.display_name or "",
                        username=user.user.slug or user.user.name,
                    )
                    for user in pr.reviewers
                ],
                source_branch=BranchRefSchema(
                    ref=pr.from_ref.display_id,
                    sha=pr.from_ref.latest_commit,
                ),
                target_branch=BranchRefSchema(
                    ref=pr.to_ref.display_id,
                    sha=pr.to_ref.latest_commit,
                ),
                changed_files=[
                    change.path.to_string
                    for change in changes.values
                    if change.path and change.path.to_string
                ],
            )
        except Exception as error:
            logger.exception(f"Failed to fetch PR info {self.pull_request_ref}: {error}")
            return ReviewInfoSchema()

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_comments(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            logger.info(f"Fetched general comments for {self.pull_request_ref}")

            return [
                get_review_comment_from_bitbucket_server_comment(comment)
                for comment in response.values
                if comment.anchor is None  # нет привязки к файлу/строке — значит общий комментарий
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch general comments for {self.pull_request_ref}: {error}")
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_comments(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            logger.info(f"Fetched inline comments for {self.pull_request_ref}")

            return [
                get_review_comment_from_bitbucket_server_comment(comment)
                for comment in response.values
                if comment.anchor is not None and comment.anchor.path is not None
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch inline comments for {self.pull_request_ref}: {error}")
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(f"Posting general comment to PR {self.pull_request_ref}: {message}")

            request = BitbucketServerCreatePRCommentRequestSchema(text=message)

            await self.http_client.pr.create_comment(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
                request=request,
            )

            logger.info(f"Created general comment in PR {self.pull_request_ref}")

        except Exception as error:
            logger.exception(f"Failed to create general comment in PR {self.pull_request_ref}: {error}")
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(f"Posting inline comment in {self.pull_request_ref} at {file}:{line}: {message}")

            anchor = BitbucketServerCommentAnchorSchema(path=file, line=line, line_type="ADDED")
            request = BitbucketServerCreatePRCommentRequestSchema(text=message, anchor=anchor)

            await self.http_client.pr.create_comment(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
                request=request,
            )

            logger.info(f"Created inline comment in {self.pull_request_ref} at {file}:{line}")

        except Exception as error:
            logger.exception(
                f"Failed to create inline comment in {self.pull_request_ref} at {file}:{line}: {error}")
            raise

    # --- Replies ---
    async def create_inline_reply(self, thread_id: int | str, message: str) -> None:
        try:
            logger.info(f"Replying to inline thread {thread_id=} in PR {self.pull_request_ref}")
            request = BitbucketServerCreatePRCommentRequestSchema(
                text=message,
                parent=BitbucketServerCommentParentSchema(id=int(thread_id)),
            )
            await self.http_client.pr.create_comment(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
                request=request,
            )
            logger.info(f"Created inline reply to thread {thread_id=} in PR {self.pull_request_ref}")
        except Exception as error:
            logger.exception(
                f"Failed to create inline reply to thread {thread_id=} in PR {self.pull_request_ref}: {error}"
            )
            raise

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        try:
            logger.info(f"Replying to summary thread {thread_id=} in PR {self.pull_request_ref}")
            request = BitbucketServerCreatePRCommentRequestSchema(
                text=message,
                parent=BitbucketServerCommentParentSchema(id=int(thread_id)),
            )
            await self.http_client.pr.create_comment(
                project_key=self.project_key,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
                request=request,
            )
            logger.info(f"Created summary reply to thread {thread_id=} in PR {self.pull_request_ref}")
        except Exception as error:
            logger.exception(
                f"Failed to create summary reply to thread {thread_id=} in PR {self.pull_request_ref}: {error}"
            )
            raise

    # --- Threads ---
    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        try:
            comments = await self.get_inline_comments()

            threads_by_id: dict[str | int, list[ReviewCommentSchema]] = defaultdict(list)
            for comment in comments:
                if not comment.file:
                    continue
                threads_by_id[comment.thread_id].append(comment)

            logger.info(f"Built {len(threads_by_id)} inline threads for {self.pull_request_ref}")

            threads: list[ReviewThreadSchema] = []
            for thread_id, thread in threads_by_id.items():
                file = thread[0].file
                line = thread[0].line
                if not file:
                    continue

                threads.append(
                    ReviewThreadSchema(
                        id=thread_id,
                        kind=ThreadKind.INLINE,
                        file=file,
                        line=line,
                        comments=sorted(thread, key=lambda c: int(c.id)),
                    )
                )

            return threads

        except Exception as error:
            logger.exception(f"Failed to fetch inline threads for {self.pull_request_ref}: {error}")
            return []

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        try:
            comments = await self.get_general_comments()

            threads_by_id: dict[str | int, list[ReviewCommentSchema]] = defaultdict(list)
            for comment in comments:
                threads_by_id[comment.thread_id].append(comment)

            logger.info(f"Built {len(threads_by_id)} general threads for {self.pull_request_ref}")

            return [
                ReviewThreadSchema(
                    id=thread_id,
                    kind=ThreadKind.SUMMARY,
                    comments=sorted(thread, key=lambda c: int(c.id)),
                )
                for thread_id, thread in threads_by_id.items()
            ]

        except Exception as error:
            logger.exception(f"Failed to fetch general threads for {self.pull_request_ref}: {error}")
            return []
