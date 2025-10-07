from collections import defaultdict

from ai_review.clients.github.client import get_github_http_client
from ai_review.clients.github.pr.schema.comments import (
    GitHubCreateReviewReplyRequestSchema,
    GitHubCreateReviewCommentRequestSchema
)
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.github.adapter import (
    get_review_comment_from_github_pr_comment,
    get_review_comment_from_github_issue_comment
)
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ThreadKind,
    UserSchema,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)

logger = get_logger("GITHUB_VCS_CLIENT")


class GitHubVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_github_http_client()
        self.owner = settings.vcs.pipeline.owner
        self.repo = settings.vcs.pipeline.repo
        self.pull_number = settings.vcs.pipeline.pull_number
        self.pull_request_ref = f"{self.owner}/{self.repo}#{self.pull_number}"

    # --- Review info ---
    async def get_review_info(self) -> ReviewInfoSchema:
        try:
            pr = await self.http_client.pr.get_pull_request(
                owner=self.owner, repo=self.repo, pull_number=self.pull_number
            )
            files = await self.http_client.pr.get_files(
                owner=self.owner, repo=self.repo, pull_number=self.pull_number
            )

            logger.info(
                f"Fetched PR info for {self.owner}/{self.repo}#{self.pull_number}"
            )

            return ReviewInfoSchema(
                id=pr.number,
                title=pr.title,
                description=pr.body or "",
                author=UserSchema(
                    id=pr.user.id,
                    name=pr.user.login,
                    username=pr.user.login,
                ),
                labels=[label.name for label in pr.labels if label.name],
                base_sha=pr.base.sha,
                head_sha=pr.head.sha,
                assignees=[
                    UserSchema(id=user.id, name=user.login, username=user.login)
                    for user in pr.assignees
                ],
                reviewers=[
                    UserSchema(id=user.id, name=user.login, username=user.login)
                    for user in pr.requested_reviewers
                ],
                source_branch=BranchRefSchema(
                    ref=pr.head.ref,
                    sha=pr.head.sha,
                ),
                target_branch=BranchRefSchema(
                    ref=pr.base.ref,
                    sha=pr.base.sha,
                ),
                changed_files=[file.filename for file in files.root],
            )
        except Exception as error:
            logger.exception(
                f"Failed to fetch PR info {self.owner}/{self.repo}#{self.pull_number}: {error}"
            )
            return ReviewInfoSchema()

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_issue_comments(
                owner=self.owner,
                repo=self.repo,
                issue_number=self.pull_number,
            )
            logger.info(f"Fetched general comments for {self.pull_request_ref}")

            return [get_review_comment_from_github_issue_comment(comment) for comment in response.root]
        except Exception as error:
            logger.exception(f"Failed to fetch general comments for {self.pull_request_ref}: {error}")
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_review_comments(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
            )
            logger.info(f"Fetched inline comments for {self.pull_request_ref}")

            return [get_review_comment_from_github_pr_comment(comment) for comment in response.root]
        except Exception as error:
            logger.exception(f"Failed to fetch inline comments for {self.pull_request_ref}: {error}")
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(f"Posting general comment to PR {self.pull_request_ref}: {message}")
            await self.http_client.pr.create_issue_comment(
                owner=self.owner,
                repo=self.repo,
                issue_number=self.pull_number,
                body=message,
            )
            logger.info(f"Created general comment in PR {self.pull_request_ref}")
        except Exception as error:
            logger.exception(f"Failed to create general comment in PR {self.pull_request_ref}: {error}")
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(f"Posting inline comment in {self.pull_request_ref} at {file}:{line}: {message}")

            pr = await self.http_client.pr.get_pull_request(
                owner=self.owner, repo=self.repo, pull_number=self.pull_number
            )

            request = GitHubCreateReviewCommentRequestSchema(
                body=message,
                path=file,
                line=line,
                commit_id=pr.head.sha
            )
            await self.http_client.pr.create_review_comment(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
                request=request,
            )
            logger.info(f"Created inline comment in {self.pull_request_ref} at {file}:{line}")
        except Exception as error:
            logger.exception(f"Failed to create inline comment in {self.pull_request_ref} at {file}:{line}: {error}")
            raise

    # --- Replies ---
    async def create_inline_reply(self, thread_id: int | str, message: str) -> None:
        try:
            logger.info(f"Replying to inline comment {thread_id=} in PR {self.pull_request_ref}")
            request = GitHubCreateReviewReplyRequestSchema(
                body=message,
                in_reply_to=thread_id
            )
            await self.http_client.pr.create_review_reply(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
                request=request,
            )
            logger.info(f"Created inline reply to comment {thread_id=} in PR {self.pull_request_ref}")
        except Exception as error:
            logger.exception(
                f"Failed to create inline reply to comment {thread_id=} in {self.pull_request_ref}: {error}"
            )
            raise

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        """
        GitHub does not support threaded replies for issue-level comments.
        We post a new top-level comment instead.
        """
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
            response = await self.http_client.pr.get_review_comments(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
            )
            comments = response.root
            logger.info(f"Fetched inline comment threads for {self.pull_request_ref}")

            threads: dict[str | int, list[ReviewCommentSchema]] = defaultdict(list)
            for comment in comments:
                review_comment = get_review_comment_from_github_pr_comment(comment)
                threads[review_comment.thread_id].append(review_comment)

            logger.info(f"Built {len(threads)} inline threads for {self.pull_request_ref}")

            return [
                ReviewThreadSchema(
                    id=thread_id,
                    kind=ThreadKind.INLINE,
                    file=thread[0].file,
                    line=thread[0].line,
                    comments=sorted(thread, key=lambda t: int(t.id)),
                )
                for thread_id, thread in threads.items()
            ]
        except Exception as error:
            logger.exception(f"Failed to fetch inline threads for {self.pull_request_ref}: {error}")
            return []

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        try:
            comments = await self.get_general_comments()

            threads = [
                ReviewThreadSchema(id=comment.thread_id, kind=ThreadKind.SUMMARY, comments=[comment])
                for comment in comments
            ]
            logger.info(f"Built {len(threads)} general threads for {self.pull_request_ref}")
            return threads
        except Exception as error:
            logger.exception(f"Failed to build general threads for {self.pull_request_ref}: {error}")
            return []
