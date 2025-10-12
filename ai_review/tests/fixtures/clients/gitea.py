import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.gitea.pr.schema.comments import (
    GiteaPRCommentSchema,
    GiteaGetPRCommentsResponseSchema,
    GiteaCreateCommentRequestSchema,
    GiteaCreateCommentResponseSchema,
)
from ai_review.clients.gitea.pr.schema.files import (
    GiteaGetPRFilesResponseSchema,
    GiteaPRFileSchema,
)
from ai_review.clients.gitea.pr.schema.pull_request import (
    GiteaGetPRResponseSchema,
    GiteaBranchSchema,
)
from ai_review.clients.gitea.pr.schema.user import GiteaUserSchema
from ai_review.clients.gitea.pr.types import GiteaPullRequestsHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.vcs.base import GiteaVCSConfig
from ai_review.libs.config.vcs.gitea import GiteaPipelineConfig, GiteaHTTPClientConfig
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.gitea.client import GiteaVCSClient


class FakeGiteaPullRequestsHTTPClient(GiteaPullRequestsHTTPClientProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def get_pull_request(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRResponseSchema:
        self.calls.append(("get_pull_request", {"owner": owner, "repo": repo, "pull_number": pull_number}))
        return GiteaGetPRResponseSchema(
            id=1,
            number=1,
            title="Fake Gitea PR",
            body="This is a fake PR for testing",
            user=GiteaUserSchema(id=101, login="tester"),
            base=GiteaBranchSchema(ref="main", sha="abc123"),
            head=GiteaBranchSchema(ref="feature", sha="def456"),
        )

    async def get_files(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRFilesResponseSchema:
        self.calls.append(("get_files", {"owner": owner, "repo": repo, "pull_number": pull_number}))
        return GiteaGetPRFilesResponseSchema(
            root=[
                GiteaPRFileSchema(
                    status="modified",
                    filename="src/main.py",
                    patch="@@ -1,2 +1,2 @@\n- old\n+ new",
                ),
                GiteaPRFileSchema(
                    status="added",
                    filename="utils/helper.py",
                    patch="+ print('Hello')",
                ),
            ]
        )

    async def get_comments(self, owner: str, repo: str, pull_number: str) -> GiteaGetPRCommentsResponseSchema:
        self.calls.append(("get_comments", {"owner": owner, "repo": repo, "pull_number": pull_number}))
        return GiteaGetPRCommentsResponseSchema(
            root=[
                GiteaPRCommentSchema(
                    id=1,
                    body="General comment",
                    user=GiteaUserSchema(id=201, login="alice"),
                ),
                GiteaPRCommentSchema(
                    id=2,
                    body="Inline comment",
                    path="file.py",
                    line=5,
                    user=GiteaUserSchema(id=202, login="bob"),
                ),
            ]
        )

    async def create_comment(
            self,
            owner: str,
            repo: str,
            pull_number: str,
            request: GiteaCreateCommentRequestSchema
    ) -> GiteaCreateCommentResponseSchema:
        self.calls.append(
            (
                "create_comment",
                {"owner": owner, "repo": repo, "pull_number": pull_number, **request.model_dump()},
            )
        )
        return GiteaCreateCommentResponseSchema(id=10, body=request.body)


class FakeGiteaHTTPClient:
    def __init__(self, pull_requests_client: FakeGiteaPullRequestsHTTPClient):
        self.pr = pull_requests_client


@pytest.fixture
def fake_gitea_pull_requests_http_client() -> FakeGiteaPullRequestsHTTPClient:
    return FakeGiteaPullRequestsHTTPClient()


@pytest.fixture
def fake_gitea_http_client(
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient
) -> FakeGiteaHTTPClient:
    return FakeGiteaHTTPClient(pull_requests_client=fake_gitea_pull_requests_http_client)


@pytest.fixture
def gitea_vcs_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_gitea_http_client: FakeGiteaHTTPClient
) -> GiteaVCSClient:
    monkeypatch.setattr(
        "ai_review.services.vcs.gitea.client.get_gitea_http_client",
        lambda: fake_gitea_http_client,
    )
    return GiteaVCSClient()


@pytest.fixture
def gitea_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = GiteaVCSConfig(
        provider=VCSProvider.GITEA,
        pipeline=GiteaPipelineConfig(
            repo="repo",
            owner="owner",
            pull_number="1",
        ),
        http_client=GiteaHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://gitea.example.com"),
            api_token=SecretStr("fake-token"),
        ),
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
