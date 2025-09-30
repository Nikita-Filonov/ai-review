from ai_review.clients.github.client import get_github_http_client
from ai_review.clients.github.pr.schema.comments import GitHubCreateReviewCommentRequestSchema
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    UserSchema,
    BranchRefSchema,
    ReviewInfoSchema,
    ReviewCommentSchema,
)

logger = get_logger("GITHUB_VCS_CLIENT")


class GitHubVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_github_http_client()
        self.owner = settings.vcs.pipeline.owner
        self.repo = settings.vcs.pipeline.repo
        self.pull_number = settings.vcs.pipeline.pull_number

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

    # === GENERAL COMMENTS ===
    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_issue_comments(
                owner=self.owner,
                repo=self.repo,
                issue_number=self.pull_number,
            )
            logger.info(
                f"Fetched general comments for {self.owner}/{self.repo}#{self.pull_number}"
            )

            return [
                ReviewCommentSchema(id=comment.id, body=comment.body or "")
                for comment in response.root
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch general comments for {self.owner}/{self.repo}#{self.pull_number}: {error}"
            )
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_review_comments(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
            )
            logger.info(
                f"Fetched inline comments for {self.owner}/{self.repo}#{self.pull_number}"
            )

            return [
                ReviewCommentSchema(
                    id=comment.id,
                    body=comment.body or "",
                    file=comment.path,
                    line=comment.line,
                )
                for comment in response.root
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch inline comments for {self.owner}/{self.repo}#{self.pull_number}: {error}"
            )
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(
                f"Posting general comment to PR {self.owner}/{self.repo}#{self.pull_number}: {message}"
            )
            await self.http_client.pr.create_issue_comment(
                owner=self.owner,
                repo=self.repo,
                issue_number=self.pull_number,
                body=message,
            )
            logger.info(
                f"Created general comment in PR {self.owner}/{self.repo}#{self.pull_number}"
            )
        except Exception as error:
            logger.exception(
                f"Failed to create general comment in PR {self.owner}/{self.repo}#{self.pull_number}: {error}"
            )
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(
                f"Posting inline comment in {self.owner}/{self.repo}#{self.pull_number} "
                f"at {file}:{line}: {message}"
            )

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
            logger.info(
                f"Created inline comment in {self.owner}/{self.repo}#{self.pull_number} at {file}:{line}"
            )
        except Exception as error:
            logger.exception(
                f"Failed to create inline comment in {self.owner}/{self.repo}#{self.pull_number} "
                f"at {file}:{line}: {error}"
            )
            raise
