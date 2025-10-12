from ai_review.clients.gitea.client import get_gitea_http_client
from ai_review.clients.gitea.pr.schema.comments import GiteaCreateCommentRequestSchema
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.gitea.adapter import (
    get_user_from_gitea_user,
    get_review_comment_from_gitea_comment,
)
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ThreadKind,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)

logger = get_logger("GITEA_VCS_CLIENT")


class GiteaVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_gitea_http_client()
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

            logger.info(f"Fetched PR info for {self.pull_request_ref}")

            return ReviewInfoSchema(
                id=pr.number,
                title=pr.title,
                description=pr.body or "",
                author=get_user_from_gitea_user(pr.user),
                labels=[],
                base_sha=pr.base.sha,
                head_sha=pr.head.sha,
                assignees=[],
                reviewers=[],
                source_branch=BranchRefSchema(ref=pr.head.ref, sha=pr.head.sha),
                target_branch=BranchRefSchema(ref=pr.base.ref, sha=pr.base.sha),
                changed_files=[file.filename for file in files.root],
            )
        except Exception as error:
            logger.exception(f"Failed to fetch PR info {self.pull_request_ref}: {error}")
            return ReviewInfoSchema()

    # --- Comments ---
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_comments(
                owner=self.owner, repo=self.repo, pull_number=self.pull_number
            )
            logger.info(f"Fetched comments for {self.pull_request_ref}")

            return [get_review_comment_from_gitea_comment(comment) for comment in response.root]
        except Exception as error:
            logger.exception(f"Failed to fetch comments for {self.pull_request_ref}: {error}")
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        comments = await self.get_general_comments()
        if comments:
            logger.warning(
                f"Gitea API does not support inline comments — "
                f"returning {len(comments)} general comments as fallback inline comments"
            )
        return comments

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(f"Posting general comment to PR {self.pull_request_ref}: {message}")
            request = GiteaCreateCommentRequestSchema(body=message)
            await self.http_client.pr.create_comment(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
                request=request,
            )
            logger.info(f"Created general comment in PR {self.pull_request_ref}")
        except Exception as error:
            logger.exception(f"Failed to create general comment in PR {self.pull_request_ref}: {error}")
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        fallback_message = f"[{file}:{line}] {message}"
        logger.warning(
            f"Gitea does not support inline comments. "
            f"Falling back to general comment: {fallback_message}"
        )
        await self.create_general_comment(fallback_message)

    async def create_inline_reply(self, thread_id: int | str, message: str) -> None:
        logger.warning("Gitea does not support threaded replies — posting new general comment instead")
        await self.create_general_comment(message)

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        await self.create_general_comment(message)

    # --- Threads ---
    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        try:
            comments = await self.get_inline_comments()
            return [
                ReviewThreadSchema(
                    id=comment.thread_id,
                    kind=ThreadKind.INLINE,
                    file=comment.file,
                    line=comment.line,
                    comments=[comment],
                )
                for comment in comments
            ]
        except Exception as error:
            logger.exception(f"Failed to build inline threads for {self.pull_request_ref}: {error}")
            return []

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        try:
            comments = await self.get_general_comments()
            return [
                ReviewThreadSchema(
                    id=comment.thread_id,
                    kind=ThreadKind.SUMMARY,
                    comments=[comment],
                )
                for comment in comments
            ]
        except Exception as error:
            logger.exception(f"Failed to build general threads for {self.pull_request_ref}: {error}")
            return []
