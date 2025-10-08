import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.github.pr.schema.comments import (
    GitHubPRCommentSchema,
    GitHubIssueCommentSchema,
    GitHubGetPRCommentsResponseSchema,
    GitHubGetIssueCommentsResponseSchema,
    GitHubCreateIssueCommentResponseSchema,
    GitHubCreateReviewReplyRequestSchema,
    GitHubCreateReviewCommentRequestSchema,
    GitHubCreateReviewCommentResponseSchema,
)
from ai_review.clients.github.pr.schema.files import GitHubGetPRFilesResponseSchema, GitHubPRFileSchema
from ai_review.clients.github.pr.schema.pull_request import (
    GitHubUserSchema,
    GitHubLabelSchema,
    GitHubBranchSchema,
    GitHubGetPRResponseSchema,
)
from ai_review.clients.github.pr.schema.reviews import GitHubGetPRReviewsResponseSchema, GitHubPRReviewSchema
from ai_review.clients.github.pr.types import GitHubPullRequestsHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.vcs.base import GitHubVCSConfig
from ai_review.libs.config.vcs.github import GitHubPipelineConfig, GitHubHTTPClientConfig
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.github.client import GitHubVCSClient


class FakeGitHubPullRequestsHTTPClient(GitHubPullRequestsHTTPClientProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def get_pull_request(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRResponseSchema:
        self.calls.append(("get_pull_request", {"owner": owner, "repo": repo, "pull_number": pull_number}))
        return GitHubGetPRResponseSchema(
            id=1,
            number=1,
            title="Fake Pull Request",
            body="This is a fake PR for testing",
            user=GitHubUserSchema(id=101, login="tester"),
            labels=[
                GitHubLabelSchema(id=1, name="bugfix"),
                GitHubLabelSchema(id=2, name="backend"),
            ],
            assignees=[
                GitHubUserSchema(id=102, login="dev1"),
                GitHubUserSchema(id=103, login="dev2"),
            ],
            requested_reviewers=[
                GitHubUserSchema(id=104, login="reviewer"),
            ],
            base=GitHubBranchSchema(ref="main", sha="abc123"),
            head=GitHubBranchSchema(ref="feature/test", sha="def456"),
        )

    async def get_files(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRFilesResponseSchema:
        self.calls.append(("get_files", {"owner": owner, "repo": repo, "pull_number": pull_number}))

        return GitHubGetPRFilesResponseSchema(
            root=[
                GitHubPRFileSchema(
                    sha="abc",
                    status="modified",
                    filename="app/main.py",
                    patch="@@ -1,2 +1,2 @@\n- old\n+ new",
                ),
                GitHubPRFileSchema(
                    sha="def",
                    status="added",
                    filename="utils/helper.py",
                    patch="+ print('Hello')",
                ),
            ]
        )

    async def get_issue_comments(
            self,
            owner: str,
            repo: str,
            issue_number: str
    ) -> GitHubGetIssueCommentsResponseSchema:
        self.calls.append(("get_issue_comments", {"owner": owner, "repo": repo, "issue_number": issue_number}))

        return GitHubGetIssueCommentsResponseSchema(
            root=[
                GitHubIssueCommentSchema(
                    id=1,
                    body="General comment",
                    user=GitHubUserSchema(id=201, login="alice")
                ),
                GitHubIssueCommentSchema(
                    id=2,
                    body="Another general comment",
                    user=GitHubUserSchema(id=202, login="bob"),
                ),
            ]
        )

    async def get_review_comments(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRCommentsResponseSchema:
        self.calls.append(("get_review_comments", {"owner": owner, "repo": repo, "pull_number": pull_number}))
        return GitHubGetPRCommentsResponseSchema(
            root=[
                GitHubPRCommentSchema(id=3, body="Inline comment", path="file.py", line=5),
                GitHubPRCommentSchema(id=4, body="Another inline comment", path="utils.py", line=10),
            ]
        )

    async def get_reviews(self, owner: str, repo: str, pull_number: str) -> GitHubGetPRReviewsResponseSchema:
        self.calls.append(("get_reviews", {"owner": owner, "repo": repo, "pull_number": pull_number}))

        return GitHubGetPRReviewsResponseSchema(
            root=[
                GitHubPRReviewSchema(id=1, body="Looks good", state="APPROVED"),
                GitHubPRReviewSchema(id=2, body="Needs changes", state="CHANGES_REQUESTED"),
            ]
        )

    async def create_review_reply(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GitHubCreateReviewReplyRequestSchema,
    ) -> GitHubCreateReviewCommentResponseSchema:
        self.calls.append(
            (
                "create_review_reply",
                {"owner": owner, "repo": repo, "pull_number": pull_number, **request.model_dump()}
            )
        )
        return GitHubCreateReviewCommentResponseSchema(id=12, body=request.body)

    async def create_review_comment(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GitHubCreateReviewCommentRequestSchema,
    ) -> GitHubCreateReviewCommentResponseSchema:
        self.calls.append(
            (
                "create_review_comment",
                {"owner": owner, "repo": repo, "pull_number": pull_number, **request.model_dump()}
            )
        )
        return GitHubCreateReviewCommentResponseSchema(id=10, body=request.body)

    async def create_issue_comment(
            self,
            owner: str,
            repo: str,
            issue_number: str,
            body: str,
    ) -> GitHubCreateIssueCommentResponseSchema:
        self.calls.append(
            (
                "create_issue_comment",
                {"owner": owner, "repo": repo, "issue_number": issue_number, "body": body}
            )
        )
        return GitHubCreateIssueCommentResponseSchema(id=11, body=body)


class FakeGitHubHTTPClient:
    def __init__(self, pull_requests_client: GitHubPullRequestsHTTPClientProtocol):
        self.pr = pull_requests_client


@pytest.fixture
def fake_github_pull_requests_http_client() -> FakeGitHubPullRequestsHTTPClient:
    return FakeGitHubPullRequestsHTTPClient()


@pytest.fixture
def fake_github_http_client(
        fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient
) -> FakeGitHubHTTPClient:
    return FakeGitHubHTTPClient(pull_requests_client=fake_github_pull_requests_http_client)


@pytest.fixture
def github_vcs_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_github_http_client: FakeGitHubHTTPClient
) -> GitHubVCSClient:
    monkeypatch.setattr(
        "ai_review.services.vcs.github.client.get_github_http_client",
        lambda: fake_github_http_client,
    )

    return GitHubVCSClient()


@pytest.fixture
def github_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = GitHubVCSConfig(
        provider=VCSProvider.GITHUB,
        pipeline=GitHubPipelineConfig(
            repo="repo",
            owner="owner",
            pull_number="pull_number"
        ),
        http_client=GitHubHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://github.com"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
