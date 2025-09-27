from ai_review.clients.github.client import get_github_http_client
from ai_review.config import settings
from ai_review.libs.logger import get_logger
from ai_review.services.vcs.types import (
    VCSClient,
    MRNoteSchema,
    MRUserSchema,
    MRInfoSchema,
    MRCommentSchema,
    MRDiscussionSchema,
)

logger = get_logger("GITHUB_VCS_CLIENT")


class GitHubVCSClient(VCSClient):
    def __init__(self):
        self.http_client = get_github_http_client()
        self.owner = settings.vcs.pipeline.owner
        self.repo = settings.vcs.pipeline.repo
        self.pull_number = settings.vcs.pipeline.pull_number

    async def get_mr_info(self) -> MRInfoSchema:
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

            return MRInfoSchema(
                title=pr.title,
                author=MRUserSchema(
                    name=pr.user.login,
                    username=pr.user.login,
                ),
                labels=[label.name for label in pr.labels],
                base_sha=pr.base.sha,
                head_sha=pr.head.sha,
                assignees=[
                    MRUserSchema(name=user.login, username=user.login)
                    for user in pr.assignees
                ],
                reviewers=[
                    MRUserSchema(name=user.login, username=user.login)
                    for user in pr.requested_reviewers
                ],
                description=pr.body or "",
                source_branch=pr.head.ref,
                target_branch=pr.base.ref,
                changed_files=[file.filename for file in files.root],
            )
        except Exception as error:
            logger.exception(
                f"Failed to fetch PR info {self.owner}/{self.repo}#{self.pull_number}: {error}"
            )
            return MRInfoSchema()

    async def get_comments(self) -> list[MRCommentSchema]:
        try:
            response = await self.http_client.pr.get_issue_comments(
                owner=self.owner,
                repo=self.repo,
                issue_number=self.pull_number,
            )
            logger.info(
                f"Fetched issue comments for {self.owner}/{self.repo}#{self.pull_number}"
            )

            return [MRCommentSchema(id=comment.id, body=comment.body) for comment in response.root]
        except Exception as error:
            logger.exception(
                f"Failed to fetch issue comments {self.owner}/{self.repo}#{self.pull_number}: {error}"
            )
            return []

    async def get_discussions(self) -> list[MRDiscussionSchema]:
        try:
            response = await self.http_client.pr.get_review_comments(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
            )
            logger.info(
                f"Fetched review comments for {self.owner}/{self.repo}#{self.pull_number}"
            )

            return [
                MRDiscussionSchema(
                    id=str(comment.id),
                    notes=[MRNoteSchema(id=comment.id, body=comment.body or "")]
                )
                for comment in response.root
            ]
        except Exception as error:
            logger.exception(
                f"Failed to fetch review comments {self.owner}/{self.repo}#{self.pull_number}: {error}"
            )
            return []

    async def create_comment(self, message: str) -> None:
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

    async def create_discussion(self, file: str, line: int, message: str) -> None:
        try:
            pr = await self.http_client.pr.get_pull_request(
                owner=self.owner, repo=self.repo, pull_number=self.pull_number
            )
            commit_id = pr.head.sha

            await self.http_client.pr.create_review_comment(
                owner=self.owner,
                repo=self.repo,
                pull_number=self.pull_number,
                body=message,
                path=file,
                line=line,
                commit_id=commit_id,
            )
            logger.info(
                f"Created inline comment in {self.owner}/{self.repo}#{self.pull_number} at {file}:{line}"
            )
        except Exception as error:
            logger.exception(
                f"Failed to create inline comment in {self.owner}/{self.repo}#{self.pull_number} at {file}:{line}: {error}"
            )
