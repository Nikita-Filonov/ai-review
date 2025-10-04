from ai_review.clients.bitbucket.client import get_bitbucket_http_client
from ai_review.clients.bitbucket.pr.schema.comments import (
    BitbucketCommentInlineSchema,
    BitbucketCommentContentSchema,
    BitbucketCreatePRCommentRequestSchema,
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

logger = get_logger("BITBUCKET_VCS_CLIENT")


class BitbucketVCSClient(VCSClientProtocol):
    def __init__(self):
        self.http_client = get_bitbucket_http_client()
        self.workspace = settings.vcs.pipeline.workspace
        self.repo_slug = settings.vcs.pipeline.repo_slug
        self.pull_request_id = settings.vcs.pipeline.pull_request_id

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

            logger.info(f"Fetched PR info for {self.workspace}/{self.repo_slug}#{self.pull_request_id}")

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
                        name=user.display_name,
                        username=user.nickname,
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
            logger.exception(
                f"Failed to fetch PR info {self.workspace}/{self.repo_slug}#{self.pull_request_id}: {error}"
            )
            return ReviewInfoSchema()

    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_comments(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            logger.info(f"Fetched general comments for {self.workspace}/{self.repo_slug}#{self.pull_request_id}")

            return [
                ReviewCommentSchema(id=comment.id, body=comment.content.raw)
                for comment in response.values
                if comment.inline is None
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch general comments for "
                f"{self.workspace}/{self.repo_slug}#{self.pull_request_id}: {error}"
            )
            return []

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        try:
            response = await self.http_client.pr.get_comments(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
            )
            logger.info(f"Fetched inline comments for {self.workspace}/{self.repo_slug}#{self.pull_request_id}")

            return [
                ReviewCommentSchema(
                    id=comment.id,
                    body=comment.content.raw,
                    file=comment.inline.path,
                    line=comment.inline.to_line,
                )
                for comment in response.values
                if comment.inline is not None
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch inline comments for "
                f"{self.workspace}/{self.repo_slug}#{self.pull_request_id}: {error}"
            )
            return []

    async def create_general_comment(self, message: str) -> None:
        try:
            logger.info(
                f"Posting general comment to PR {self.workspace}/{self.repo_slug}#{self.pull_request_id}: {message}"
            )
            request = BitbucketCreatePRCommentRequestSchema(
                content=BitbucketCommentContentSchema(raw=message)
            )
            await self.http_client.pr.create_comment(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
                request=request,
            )
            logger.info(
                f"Created general comment in PR {self.workspace}/{self.repo_slug}#{self.pull_request_id}"
            )
        except Exception as error:
            logger.exception(
                f"Failed to create general comment in PR "
                f"{self.workspace}/{self.repo_slug}#{self.pull_request_id}: {error}"
            )
            raise

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        try:
            logger.info(
                f"Posting inline comment in {self.workspace}/{self.repo_slug}#{self.pull_request_id} "
                f"at {file}:{line}: {message}"
            )
            request = BitbucketCreatePRCommentRequestSchema(
                content=BitbucketCommentContentSchema(raw=message),
                inline=BitbucketCommentInlineSchema(path=file, to_line=line),
            )
            await self.http_client.pr.create_comment(
                workspace=self.workspace,
                repo_slug=self.repo_slug,
                pull_request_id=self.pull_request_id,
                request=request,
            )
            logger.info(
                f"Created inline comment in {self.workspace}/{self.repo_slug}#{self.pull_request_id} "
                f"at {file}:{line}"
            )
        except Exception as error:
            logger.exception(
                f"Failed to create inline comment in {self.workspace}/{self.repo_slug}#{self.pull_request_id} "
                f"at {file}:{line}: {error}"
            )
            raise
