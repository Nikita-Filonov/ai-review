from ai_review.clients.azure_devops.client import get_azure_devops_http_client
from ai_review.clients.azure_devops.pr.schema.files import AzureDevOpsFilePositionSchema
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsThreadContextSchema,
    AzureDevOpsIterationContextSchema,
    AzureDevOpsCreatePRThreadRequestSchema,
    AzureDevOpsCreatePRCommentRequestSchema,
    AzureDevOpsPullRequestThreadContextSchema,
)
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.azure_devops.adapter import get_review_comment_from_azure_devops_comment
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ThreadKind,
    UserSchema,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)

logger = get_logger("AZURE_DEVOPS_VCS_CLIENT")


class AzureDevOpsVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_azure_devops_http_client()
        self.organization = settings.vcs.pipeline.organization
        self.project = settings.vcs.pipeline.project
        self.repository_id = settings.vcs.pipeline.repository_id
        self.pull_request_id = settings.vcs.pipeline.pull_request_id
        self.iteration_id = settings.vcs.pipeline.iteration_id
        self.pull_request_ref = (
            f"{self.organization}/{self.project}/{self.repository_id}#{self.pull_request_id}"
        )

    # --- Review info ---
    async def get_review_info(self) -> ReviewInfoSchema:
        try:
            pr = await self.http_client.pr.get_pull_request(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
            )

            files = await self.http_client.pr.get_files(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
                iteration_id=self.iteration_id,
            )

            logger.info(
                f"Fetched PR info for {self.pull_request_ref}"
            )

            return ReviewInfoSchema(
                id=pr.pull_request_id,
                title=pr.title or "",
                description=pr.description or "",
                author=UserSchema(
                    id=pr.created_by.id,
                    name=pr.created_by.display_name,
                    username=pr.created_by.unique_name,
                ),
                reviewers=[
                    UserSchema(
                        id=reviewer.id,
                        name=reviewer.display_name,
                        username=reviewer.unique_name,
                    )
                    for reviewer in pr.reviewers
                ],
                source_branch=BranchRefSchema(
                    ref=pr.source_ref_name,
                    sha=pr.last_merge_source_commit.commit_id if pr.last_merge_source_commit else None,
                ),
                target_branch=BranchRefSchema(
                    ref=pr.target_ref_name,
                    sha=pr.last_merge_target_commit.commit_id if pr.last_merge_target_commit else None,
                ),
                changed_files=[
                    change.item.path for change in files.change_entries if change.item and change.item.path
                ],
                base_sha=pr.last_merge_target_commit.commit_id if pr.last_merge_target_commit else None,
                head_sha=pr.last_merge_source_commit.commit_id if pr.last_merge_source_commit else None,
                start_sha=pr.last_merge_source_commit.commit_id if pr.last_merge_source_commit else None,
            )

        except Exception as error:
            logger.exception(
                f"Failed to fetch PR info {self.pull_request_ref}: {error}"
            )
            return ReviewInfoSchema()

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
            )

            threads = response.value
            general_threads = [t for t in threads if not t.thread_context or not t.thread_context.file_path]

            logger.info(f"Fetched {len(general_threads)} general comment threads for {self.pull_request_ref}")

            comments: list[ReviewCommentSchema] = []
            for thread in general_threads:
                for comment in thread.comments:
                    comments.append(get_review_comment_from_azure_devops_comment(comment, thread))

            return comments

        except Exception as error:
            logger.exception(f"Failed to fetch general comments for {self.pull_request_ref}: {error}")
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
            )

            threads = response.value
            inline_threads = [t for t in threads if t.thread_context and t.thread_context.file_path]

            logger.info(f"Fetched {len(inline_threads)} inline comment threads for {self.pull_request_ref}")

            comments: list[ReviewCommentSchema] = []
            for thread in inline_threads:
                for comment in thread.comments:
                    comments.append(get_review_comment_from_azure_devops_comment(comment, thread))

            return comments

        except Exception as error:
            logger.exception(f"Failed to fetch inline comments for {self.pull_request_ref}: {error}")
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(f"Posting general comment to PR {self.pull_request_ref}: {message}")

            request = AzureDevOpsCreatePRThreadRequestSchema(
                comments=[AzureDevOpsCreatePRCommentRequestSchema(content=message)],
                thread_context=None,
            )
            await self.http_client.pr.create_thread(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
                request=request,
            )

            logger.info(f"Created general comment in PR {self.pull_request_ref}")

        except Exception as error:
            logger.exception(f"Failed to create general comment in {self.pull_request_ref}: {error}")
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(f"Posting inline comment in {self.pull_request_ref} at {file}:{line}: {message}")

            request = AzureDevOpsCreatePRThreadRequestSchema(
                comments=[AzureDevOpsCreatePRCommentRequestSchema(content=message)],
                thread_context=AzureDevOpsThreadContextSchema(
                    file_path=file,
                    right_file_end=AzureDevOpsFilePositionSchema(line=line, offset=1),
                    right_file_start=AzureDevOpsFilePositionSchema(line=line, offset=1),
                ),
                pull_request_thread_context=AzureDevOpsPullRequestThreadContextSchema(
                    iteration_context=AzureDevOpsIterationContextSchema(
                        first_comparing_iteration=self.iteration_id,
                        second_comparing_iteration=self.iteration_id,
                    ),
                    change_tracking_id=1,
                ),
            )

            await self.http_client.pr.create_thread(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
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

            request = AzureDevOpsCreatePRCommentRequestSchema(content=message)

            await self.http_client.pr.create_comment(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
                thread_id=int(thread_id),
                request=request,
            )

            logger.info(f"Created inline reply in thread {thread_id=} for {self.pull_request_ref}")

        except Exception as error:
            logger.exception(
                f"Failed to create inline reply in thread {thread_id=} for {self.pull_request_ref}: {error}"
            )
            raise

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        try:
            logger.info(f"Replying to general comment {thread_id=} in PR {self.pull_request_ref}")
            await self.create_general_comment(message)
        except Exception as error:
            logger.exception(
                f"Failed to create summary reply to comment {thread_id=} in {self.pull_request_ref}: {error}"
            )
            raise

    # --- Threads ---
    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
            )

            threads_data = [
                thread for thread in response.value
                if thread.thread_context and thread.thread_context.file_path
            ]

            logger.info(f"Fetched {len(threads_data)} inline threads for {self.pull_request_ref}")

            review_threads: list[ReviewThreadSchema] = []
            for thread in threads_data:
                comments = [
                    get_review_comment_from_azure_devops_comment(comment, thread)
                    for comment in thread.comments
                ]
                review_threads.append(
                    ReviewThreadSchema(
                        id=thread.id,
                        kind=ThreadKind.INLINE,
                        file=thread.thread_context.file_path,
                        line=(
                            thread.thread_context.right_file_start.line
                            if thread.thread_context and thread.thread_context.right_file_start
                            else None
                        ),
                        comments=sorted(comments, key=lambda c: int(c.id)),
                    )
                )

            logger.info(f"Built {len(review_threads)} inline threads for {self.pull_request_ref}")
            return review_threads

        except Exception as error:
            logger.exception(f"Failed to fetch inline threads for {self.pull_request_ref}: {error}")
            return []

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        try:
            response = await self.http_client.pr.get_threads(
                organization=self.organization,
                project=self.project,
                repository_id=self.repository_id,
                pull_request_id=self.pull_request_id,
            )

            threads_data = [
                thread for thread in response.value
                if (not thread.thread_context) or (not thread.thread_context.file_path)
            ]

            logger.info(f"Fetched {len(threads_data)} general threads for {self.pull_request_ref}")

            review_threads: list[ReviewThreadSchema] = []

            for thread in threads_data:
                comments = [
                    get_review_comment_from_azure_devops_comment(comment, thread)
                    for comment in thread.comments
                ]
                review_threads.append(
                    ReviewThreadSchema(
                        id=thread.id,
                        kind=ThreadKind.SUMMARY,
                        comments=sorted(comments, key=lambda c: int(c.id)),
                    )
                )

            logger.info(f"Built {len(review_threads)} general threads for {self.pull_request_ref}")
            return review_threads

        except Exception as error:
            logger.exception(f"Failed to build general threads for {self.pull_request_ref}: {error}")
            return []
