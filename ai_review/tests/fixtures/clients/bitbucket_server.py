import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.bitbucket_server.pr.schema.changes import (
    BitbucketServerChangeSchema,
    BitbucketServerChangePathSchema,
    BitbucketServerGetPRChangesResponseSchema,
)
from ai_review.clients.bitbucket_server.pr.schema.comments import (
    BitbucketServerCommentSchema,
    BitbucketServerCommentAnchorSchema,
    BitbucketServerGetPRCommentsResponseSchema,
    BitbucketServerCreatePRCommentRequestSchema,
    BitbucketServerCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket_server.pr.schema.pull_request import (
    BitbucketServerRefSchema,
    BitbucketServerUserSchema,
    BitbucketServerProjectSchema,
    BitbucketServerRepositorySchema,
    BitbucketServerParticipantSchema,
    BitbucketServerGetPRResponseSchema,
)
from ai_review.clients.bitbucket_server.pr.types import BitbucketServerPullRequestsHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.vcs.base import BitbucketServerVCSConfig
from ai_review.libs.config.vcs.bitbucket_server import BitbucketServerPipelineConfig, BitbucketServerHTTPClientConfig
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.bitbucket_server.client import BitbucketServerVCSClient


class FakeBitbucketServerPullRequestsHTTPClient(BitbucketServerPullRequestsHTTPClientProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def get_pull_request(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int
    ) -> BitbucketServerGetPRResponseSchema:
        self.calls.append(
            (
                "get_pull_request",
                {
                    "project_key": project_key,
                    "repo_slug": repo_slug,
                    "pull_request_id": pull_request_id
                }
            )
        )
        return BitbucketServerGetPRResponseSchema(
            id=1,
            version=1,
            title="Fake Bitbucket Server PR",
            description="PR for testing server client",
            state="OPEN",
            open=True,
            locked=False,
            author=BitbucketServerParticipantSchema(
                user=BitbucketServerUserSchema(
                    id=100,
                    name="author",
                    slug="author",
                    display_name="Author User",
                ),
                role="AUTHOR",
            ),
            reviewers=[
                BitbucketServerParticipantSchema(
                    user=BitbucketServerUserSchema(
                        id=101,
                        name="reviewer",
                        slug="reviewer",
                        display_name="Reviewer User",
                    ),
                    role="REVIEWER",
                )
            ],
            from_ref=BitbucketServerRefSchema(
                id="refs/heads/feature/test",
                display_id="feature/test",
                latest_commit="def456",
                repository=BitbucketServerRepositorySchema(
                    slug="repo",
                    name="Repo Name",
                    project=BitbucketServerProjectSchema(key="PRJ"),
                ),
            ),
            to_ref=BitbucketServerRefSchema(
                id="refs/heads/main",
                display_id="main",
                latest_commit="abc123",
                repository=BitbucketServerRepositorySchema(
                    slug="repo",
                    name="Repo Name",
                    project=BitbucketServerProjectSchema(key="PRJ"),
                ),
            ),
            created_date=1690000000,
            updated_date=1690000100,
            links={},
        )

    async def get_changes(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int
    ) -> BitbucketServerGetPRChangesResponseSchema:
        self.calls.append(
            (
                "get_changes", {
                    "project_key": project_key,
                    "repo_slug": repo_slug,
                    "pull_request_id": pull_request_id
                }
            )
        )
        return BitbucketServerGetPRChangesResponseSchema(
            size=1,
            start=0,
            limit=100,
            is_last_page=True,
            next_page_start=None,
            values=[
                BitbucketServerChangeSchema(
                    path=BitbucketServerChangePathSchema(to_string="src/main.py"),
                    type="MODIFY",
                    src_path=None,
                    node_type="FILE",
                    executable=False,
                )
            ],
        )

    async def get_comments(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int
    ) -> BitbucketServerGetPRCommentsResponseSchema:
        self.calls.append(
            (
                "get_comments",
                {"project_key": project_key, "repo_slug": repo_slug, "pull_request_id": pull_request_id}
            )
        )
        return BitbucketServerGetPRCommentsResponseSchema(
            size=2,
            start=0,
            limit=100,
            is_last_page=True,
            next_page_start=None,
            values=[
                BitbucketServerCommentSchema(
                    id=1,
                    text="General comment",
                    author=BitbucketServerUserSchema(
                        id=100,
                        name="user1",
                        slug="user1",
                        display_name="User One",
                    ),
                    anchor=None,
                    comments=[],
                    created_date=1690000000,
                    updated_date=1690000000,
                ),
                BitbucketServerCommentSchema(
                    id=2,
                    text="Inline comment",
                    author=BitbucketServerUserSchema(
                        id=101,
                        name="user2",
                        slug="user2",
                        display_name="User Two",
                    ),
                    anchor=BitbucketServerCommentAnchorSchema(path="src/main.py", line=5, line_type="ADDED"),
                    comments=[],
                    created_date=1690000001,
                    updated_date=1690000001,
                ),
            ],
        )

    async def create_comment(
            self,
            project_key: str,
            repo_slug: str,
            pull_request_id: int,
            request: BitbucketServerCreatePRCommentRequestSchema
    ) -> BitbucketServerCreatePRCommentResponseSchema:
        self.calls.append(
            (
                "create_comment",
                {
                    "project_key": project_key,
                    "repo_slug": repo_slug,
                    "pull_request_id": pull_request_id,
                    **request.model_dump(by_alias=True)
                }
            )
        )
        return BitbucketServerCreatePRCommentResponseSchema(
            id=10,
            text=request.text,
            author=BitbucketServerUserSchema(
                id=999,
                name="bot",
                slug="bot",
                display_name="Automation Bot",
            ),
            anchor=request.anchor,
            comments=[],
            created_date=1690000200,
            updated_date=1690000200,
        )


class FakeBitbucketServerHTTPClient:
    def __init__(self, pull_requests_client: BitbucketServerPullRequestsHTTPClientProtocol):
        self.pr = pull_requests_client


@pytest.fixture
def fake_bitbucket_server_pull_requests_http_client() -> FakeBitbucketServerPullRequestsHTTPClient:
    return FakeBitbucketServerPullRequestsHTTPClient()


@pytest.fixture
def fake_bitbucket_server_http_client(
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient
) -> FakeBitbucketServerHTTPClient:
    return FakeBitbucketServerHTTPClient(pull_requests_client=fake_bitbucket_server_pull_requests_http_client)


@pytest.fixture
def bitbucket_server_vcs_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_bitbucket_server_http_client: FakeBitbucketServerHTTPClient
) -> BitbucketServerVCSClient:
    monkeypatch.setattr(
        "ai_review.services.vcs.bitbucket_server.client.get_bitbucket_server_http_client",
        lambda: fake_bitbucket_server_http_client,
    )
    return BitbucketServerVCSClient()


@pytest.fixture
def bitbucket_server_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = BitbucketServerVCSConfig(
        provider=VCSProvider.BITBUCKET_SERVER,
        pipeline=BitbucketServerPipelineConfig(
            project_key="PRJ",
            repo_slug="repo",
            pull_request_id=1,
        ),
        http_client=BitbucketServerHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://bitbucket.server.local/rest/api/1.0"),
            api_token=SecretStr("fake-token"),
        ),
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
