from collections import defaultdict

from ai_review.clients.bitbucket_cloud.client import get_bitbucket_cloud_http_client
from ai_review.clients.bitbucket_cloud.pr.schema.comments import (
    BitbucketCloudCommentParentSchema,
    BitbucketCloudCommentInlineSchema,
    BitbucketCloudCommentContentSchema,
    BitbucketCloudCreatePRCommentRequestSchema,
)
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.bitbucket_cloud.adapter import get_review_comment_from_bitbucket_pr_comment
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ThreadKind,
    UserSchema,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)

logger = get_logger("BITBUCKET_CLOUD_VCS_CLIENT")


class BitbucketCloudVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_bitbucket_cloud_http_client()
        self.workspace = settings.vcs.pipeline.workspace
        self.repo_slug = settings.vcs.pipeline.repo_slug
        self.pull_request_id = settings.vcs.pipeline.pull_request_id
        self.pull_request_ref = f"{self.workspace}/{self.repo_slug}#{self.pull_request_id}"

    # --- Review info ---
    async def get_review_info(self) -> ReviewInfoSchema:
        try:
            pr = await self.http_client.pr.get_pull_request(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            files = await self.http_client.pr.get_files(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )

            logger.info(f"Fetched PR info for {self.pull_request_ref}")

            return ReviewInfoSchema(
                id=pr.id,
                title=pr.title,
                description=pr.description or "",
                author=UserSchema(
                    id=pr.author.uuid,
                    name=pr.author.display_name,
                    username=pr.author.nickname,
                ),
                labels=[],
                base_sha=pr.destination.commit.hash,
                head_sha=pr.source.commit.hash,
                assignees=[
                    UserSchema(
                        id=user.uuid,
                        name=user.display_name or "",
                        username=user.nickname or "",
                    )
                    for user in pr.participants
                ],
                reviewers=[
                    UserSchema(
                        id=user.uuid,
                        name=user.display_name,
                        username=user.nickname,
                    )
                    for user in pr.reviewers
                ],
                source_branch=BranchRefSchema(
                    ref=pr.source.branch.name,
                    sha=pr.source.commit.hash,
                ),
                target_branch=BranchRefSchema(
                    ref=pr.destination.branch.name,
                    sha=pr.destination.commit.hash,
                ),
                changed_files=[
                    file.new.path if file.new else file.old.path
                    for file in files.values
                ],
            )
        except Exception as error:
            logger.exception(f"Failed to fetch PR info {self.pull_request_ref}: {error}")
            return ReviewInfoSchema()

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_comments(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            logger.info(f"Fetched general comments for {self.pull_request_ref}")

            return [
                get_review_comment_from_bitbucket_pr_comment(comment)
                for comment in response.values
                if comment.inline is None
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch general comments for {self.pull_request_ref}: {error}")
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_comments(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            logger.info(f"Fetched inline comments for {self.pull_request_ref}")

            return [
                get_review_comment_from_bitbucket_pr_comment(comment)
                for comment in response.values
                if comment.inline is not None
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch inline comments for {self.pull_request_ref}: {error}")
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(f"Posting general comment to PR {self.pull_request_ref}: {message}")
            request = BitbucketCloudCreatePRCommentRequestSchema(
                content=BitbucketCloudCommentContentSchema(raw=message)
            )
            await self.http_client.pr.create_comment(
                workspace=self.workspace,
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
            request = BitbucketCloudCreatePRCommentRequestSchema(
                content=BitbucketCloudCommentContentSchema(raw=message),
                inline=BitbucketCloudCommentInlineSchema(path=file, to_line=line),
            )
            await self.http_client.pr.create_comment(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
                request=request,
            )
            logger.info(f"Created inline comment in {self.pull_request_ref} at {file}:{line}")
        except Exception as error:
            logger.exception(f"Failed to create inline comment in {self.pull_request_ref} at {file}:{line}: {error}")
            raise

    # --- Replies ---
    async def create_inline_reply(self, thread_id: int | str, message: str) -> None:
        try:
            logger.info(f"Replying to inline thread {thread_id=} in PR {self.pull_request_ref}")
            request = BitbucketCloudCreatePRCommentRequestSchema(
                parent=BitbucketCloudCommentParentSchema(id=int(thread_id)),
                content=BitbucketCloudCommentContentSchema(raw=message),
            )
            await self.http_client.pr.create_comment(
                workspace=self.workspace,
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
            request = BitbucketCloudCreatePRCommentRequestSchema(
                content=BitbucketCloudCommentContentSchema(raw=message),
                parent=BitbucketCloudCommentParentSchema(id=int(thread_id)),
            )
            await self.http_client.pr.create_comment(
                workspace=self.workspace,
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
                        comments=sorted(thread, key=lambda t: int(t.id)),
                    )
                )

            return threads
        except Exception as error:
            logger.exception(f"Failed to fetch inline threads for {self.pull_request_ref}: {error}")
            return []

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        try:
            comments = await self.get_general_comments()

            threads: dict[str | int, list[ReviewCommentSchema]] = defaultdict(list)
            for comment in comments:
                threads[comment.thread_id].append(comment)

            logger.info(f"Built {len(threads)} general threads for {self.pull_request_ref}")

            return [
                ReviewThreadSchema(
                    id=thread_id,
                    kind=ThreadKind.SUMMARY,
                    comments=sorted(thread, key=lambda c: int(c.id)),
                )
                for thread_id, thread in threads.items()
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch general threads for {self.pull_request_ref}: {error}")
            return []
