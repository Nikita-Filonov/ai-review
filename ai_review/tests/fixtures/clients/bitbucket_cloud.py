import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.bitbucket_cloud.pr.schema.comments import (
    BitbucketCloudPRCommentSchema,
    BitbucketCloudCommentContentSchema,
    BitbucketCloudCommentInlineSchema,
    BitbucketCloudGetPRCommentsResponseSchema,
    BitbucketCloudCreatePRCommentRequestSchema,
    BitbucketCloudCreatePRCommentResponseSchema,
)
from ai_review.clients.bitbucket_cloud.pr.schema.files import (
    BitbucketCloudGetPRFilesResponseSchema,
    BitbucketCloudPRFileSchema,
    BitbucketCloudPRFilePathSchema,
)
from ai_review.clients.bitbucket_cloud.pr.schema.pull_request import (
    BitbucketCloudUserSchema,
    BitbucketCloudBranchSchema,
    BitbucketCloudCommitSchema,
    BitbucketCloudRepositorySchema,
    BitbucketCloudPRLocationSchema,
    BitbucketCloudGetPRResponseSchema,
)
from ai_review.clients.bitbucket_cloud.pr.types import BitbucketCloudPullRequestsHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.vcs.base import BitbucketCloudVCSConfig
from ai_review.libs.config.vcs.bitbucket_cloud import (
    BitbucketCloudPipelineConfig,
    BitbucketCloudHTTPClientConfig
)
from ai_review.libs.constants.vcs_provider import VCSProvider
from ai_review.services.vcs.bitbucket_cloud.client import BitbucketCloudVCSClient


class FakeBitbucketCloudPullRequestsHTTPClient(BitbucketCloudPullRequestsHTTPClientProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def get_pull_request(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRResponseSchema:
        self.calls.append(
            (
                "get_pull_request",
                {"workspace": workspace, "repo_slug": repo_slug, "pull_request_id": pull_request_id}
            )
        )
        return BitbucketCloudGetPRResponseSchema(
            id=1,
            title="Fake Bitbucket PR",
            description="This is a fake PR for testing",
            state="OPEN",
            author=BitbucketCloudUserSchema(uuid="u1", display_name="Tester", nickname="tester"),
            source=BitbucketCloudPRLocationSchema(
                commit=BitbucketCloudCommitSchema(hash="def456"),
                branch=BitbucketCloudBranchSchema(name="feature/test"),
                repository=BitbucketCloudRepositorySchema(uuid="r1", full_name="workspace/repo"),
            ),
            destination=BitbucketCloudPRLocationSchema(
                commit=BitbucketCloudCommitSchema(hash="abc123"),
                branch=BitbucketCloudBranchSchema(name="main"),
                repository=BitbucketCloudRepositorySchema(uuid="r1", full_name="workspace/repo"),
            ),
            reviewers=[BitbucketCloudUserSchema(uuid="u2", display_name="Reviewer", nickname="reviewer")],
            participants=[BitbucketCloudUserSchema(uuid="u3", display_name="Participant", nickname="participant")],
        )

    async def get_files(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str
    ) -> BitbucketCloudGetPRFilesResponseSchema:
        self.calls.append(
            (
                "get_files",
                {"workspace": workspace, "repo_slug": repo_slug, "pull_request_id": pull_request_id}
            )
        )
        return BitbucketCloudGetPRFilesResponseSchema(
            size=2,
            page=1,
            page_len=100,
            next=None,
            values=[
                BitbucketCloudPRFileSchema(
                    new=BitbucketCloudPRFilePathSchema(path="app/main.py"),
                    old=None,
                    status="modified",
                    lines_added=10,
                    lines_removed=2,
                ),
                BitbucketCloudPRFileSchema(
                    new=BitbucketCloudPRFilePathSchema(path="utils/helper.py"),
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
    ) -> BitbucketCloudGetPRCommentsResponseSchema:
        self.calls.append(
            (
                "get_comments",
                {"workspace": workspace, "repo_slug": repo_slug, "pull_request_id": pull_request_id}
            )
        )
        return BitbucketCloudGetPRCommentsResponseSchema(
            size=2,
            page=1,
            next=None,
            values=[
                BitbucketCloudPRCommentSchema(
                    id=1,
                    inline=None,
                    content=BitbucketCloudCommentContentSchema(raw="General comment"),
                ),
                BitbucketCloudPRCommentSchema(
                    id=2,
                    inline=BitbucketCloudCommentInlineSchema(path="file.py", to_line=5),
                    content=BitbucketCloudCommentContentSchema(raw="Inline comment"),
                ),
            ],
            page_len=100,
        )

    async def create_comment(
            self,
            workspace: str,
            repo_slug: str,
            pull_request_id: str,
            request: BitbucketCloudCreatePRCommentRequestSchema
    ) -> BitbucketCloudCreatePRCommentResponseSchema:
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
        return BitbucketCloudCreatePRCommentResponseSchema(
            id=10,
            content=request.content,
            inline=request.inline,
        )


class FakeBitbucketCloudHTTPClient:
    def __init__(self, pull_requests_client: BitbucketCloudPullRequestsHTTPClientProtocol):
        self.pr = pull_requests_client


@pytest.fixture
def fake_bitbucket_cloud_pull_requests_http_client() -> FakeBitbucketCloudPullRequestsHTTPClient:
    return FakeBitbucketCloudPullRequestsHTTPClient()


@pytest.fixture
def fake_bitbucket_cloud_http_client(
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient
) -> FakeBitbucketCloudHTTPClient:
    return FakeBitbucketCloudHTTPClient(pull_requests_client=fake_bitbucket_cloud_pull_requests_http_client)


@pytest.fixture
def bitbucket_cloud_vcs_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_bitbucket_cloud_http_client: FakeBitbucketCloudHTTPClient
) -> BitbucketCloudVCSClient:
    monkeypatch.setattr(
        "ai_review.services.vcs.bitbucket_cloud.client.get_bitbucket_cloud_http_client",
        lambda: fake_bitbucket_cloud_http_client,
    )
    return BitbucketCloudVCSClient()


@pytest.fixture
def bitbucket_cloud_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = BitbucketCloudVCSConfig(
        provider=VCSProvider.BITBUCKET_CLOUD,
        pipeline=BitbucketCloudPipelineConfig(
            workspace="workspace",
            repo_slug="repo",
            pull_request_id="123",
        ),
        http_client=BitbucketCloudHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://api.bitbucket.org/2.0"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
