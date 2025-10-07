import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.bitbucket.pr.schema.comments import (
    BitbucketPRCommentSchema,
    BitbucketCommentContentSchema,
    BitbucketCommentInlineSchema,
    BitbucketGetPRCommentsResponseSchema,
    BitbucketCreatePRCommentRequestSchema,
    BitbucketCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket.pr.schema.files import (
    BitbucketGetPRFilesResponseSchema,
    BitbucketPRFileSchema,
    BitbucketPRFilePathSchema,
)
from ai_review.clients.bitbucket.pr.schema.pull_request import (
    BitbucketUserSchema,
    BitbucketBranchSchema,
    BitbucketCommitSchema,
    BitbucketRepositorySchema,
    BitbucketPRLocationSchema,
    BitbucketGetPRResponseSchema,
)
from ai_review.clients.bitbucket.pr.types import BitbucketPullRequestsHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.vcs.base import BitbucketVCSConfig
from ai_review.libs.config.vcs.bitbucket import BitbucketPipelineConfig, BitbucketHTTPClientConfig
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.bitbucket.client import BitbucketVCSClient


class FakeBitbucketPullRequestsHTTPClient(BitbucketPullRequestsHTTPClientProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def get_pull_request(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRResponseSchema:
        self.calls.append(
            (
                "get_pull_request",
                {"workspace": workspace, "repo_slug": repo_slug, "pull_request_id": pull_request_id}
            )
        )
        return BitbucketGetPRResponseSchema(
            id=1,
            title="Fake Bitbucket PR",
            description="This is a fake PR for testing",
            state="OPEN",
            author=BitbucketUserSchema(uuid="u1", display_name="Tester", nickname="tester"),
            source=BitbucketPRLocationSchema(
                commit=BitbucketCommitSchema(hash="def456"),
                branch=BitbucketBranchSchema(name="feature/test"),
                repository=BitbucketRepositorySchema(uuid="r1", full_name="workspace/repo"),
            ),
            destination=BitbucketPRLocationSchema(
                commit=BitbucketCommitSchema(hash="abc123"),
                branch=BitbucketBranchSchema(name="main"),
                repository=BitbucketRepositorySchema(uuid="r1", full_name="workspace/repo"),
            ),
            reviewers=[BitbucketUserSchema(uuid="u2", display_name="Reviewer", nickname="reviewer")],
            participants=[BitbucketUserSchema(uuid="u3", display_name="Participant", nickname="participant")],
        )

    async def get_files(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRFilesResponseSchema:
        self.calls.append(
            (
                "get_files",
                {"workspace": workspace, "repo_slug": repo_slug, "pull_request_id": pull_request_id}
            )
        )
        return BitbucketGetPRFilesResponseSchema(
            size=2,
            page=1,
            page_len=100,
            next=None,
            values=[
                BitbucketPRFileSchema(
                    new=BitbucketPRFilePathSchema(path="app/main.py"),
                    old=None,
                    status="modified",
                    lines_added=10,
                    lines_removed=2,
                ),
                BitbucketPRFileSchema(
                    new=BitbucketPRFilePathSchema(path="utils/helper.py"),
                    old=None,
                    status="added",
                    lines_added=5,
                    lines_removed=0,
                ),
            ],
        )

    async def get_comments(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketGetPRCommentsResponseSchema:
        self.calls.append(
            (
                "get_comments",
                {"workspace": workspace, "repo_slug": repo_slug, "pull_request_id": pull_request_id}
            )
        )
        return BitbucketGetPRCommentsResponseSchema(
            size=2,
            page=1,
            next=None,
            values=[
                BitbucketPRCommentSchema(
                    id=1,
                    inline=None,
                    content=BitbucketCommentContentSchema(raw="General comment"),
                ),
                BitbucketPRCommentSchema(
                    id=2,
                    inline=BitbucketCommentInlineSchema(path="file.py", to_line=5),
                    content=BitbucketCommentContentSchema(raw="Inline comment"),
                ),
            ],
            page_len=100,
        )

    async def create_comment(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCreatePRCommentRequestSchema
    ) -> BitbucketCreatePRCommentResponseSchema:
        self.calls.append(
            (
                "create_comment",
                {
                    "workspace": workspace,
                    "repo_slug": repo_slug,
                    "pull_request_id": pull_request_id,
                    **request.model_dump(by_alias=True)
                }
            )
        )
        return BitbucketCreatePRCommentResponseSchema(
            id=10,
            content=request.content,
            inline=request.inline,
        )


class FakeBitbucketHTTPClient:
    def __init__(self, pull_requests_client: BitbucketPullRequestsHTTPClientProtocol):
        self.pr = pull_requests_client


@pytest.fixture
def fake_bitbucket_pull_requests_http_client() -> FakeBitbucketPullRequestsHTTPClient:
    return FakeBitbucketPullRequestsHTTPClient()


@pytest.fixture
def fake_bitbucket_http_client(
        fake_bitbucket_pull_requests_http_client: FakeBitbucketPullRequestsHTTPClient
) -> FakeBitbucketHTTPClient:
    return FakeBitbucketHTTPClient(pull_requests_client=fake_bitbucket_pull_requests_http_client)


@pytest.fixture
def bitbucket_vcs_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_bitbucket_http_client: FakeBitbucketHTTPClient
) -> BitbucketVCSClient:
    monkeypatch.setattr(
        "ai_review.services.vcs.bitbucket.client.get_bitbucket_http_client",
        lambda: fake_bitbucket_http_client,
    )
    return BitbucketVCSClient()


@pytest.fixture
def bitbucket_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = BitbucketVCSConfig(
        provider=VCSProvider.BITBUCKET,
        pipeline=BitbucketPipelineConfig(
            workspace="workspace",
            repo_slug="repo",
            pull_request_id="123",
        ),
        http_client=BitbucketHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://api.bitbucket.org/2.0"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
