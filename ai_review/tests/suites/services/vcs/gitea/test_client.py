import pytest

from ai_review.services.vcs.gitea.client import GiteaVCSClient
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewCommentSchema, ReviewThreadSchema, ThreadKind
from ai_review.tests.fixtures.clients.gitea import FakeGiteaPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_review_info_returns_valid_schema(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    info = await gitea_vcs_client.get_review_info()

    assert isinstance(info, ReviewInfoSchema)
    assert info.id == 1
    assert info.title == "Fake Gitea PR"
    assert info.author.username == "tester"
    assert "src/main.py" in info.changed_files
    assert info.source_branch.ref == "feature"
    assert info.target_branch.ref == "main"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_general_comments_returns_list(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    comments = await gitea_vcs_client.get_general_comments()
    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) > 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_inline_comments_filters_by_file(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    comments = await gitea_vcs_client.get_inline_comments()
    assert all(c.file for c in comments)
    assert all(isinstance(c, ReviewCommentSchema) for c in comments)


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_create_general_comment_posts_comment(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    await gitea_vcs_client.create_general_comment("Test comment")
    calls = [name for name, _ in fake_gitea_pull_requests_http_client.calls]
    assert "create_comment" in calls


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_create_inline_comment_posts_comment(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    await gitea_vcs_client.create_inline_comment("src/main.py", 10, "Inline comment")
    calls = [name for name, _ in fake_gitea_pull_requests_http_client.calls]
    assert "create_comment" in calls


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_inline_threads_groups_by_comment(
        gitea_vcs_client: GiteaVCSClient,
):
    threads = await gitea_vcs_client.get_inline_threads()
    assert all(isinstance(t, ReviewThreadSchema) for t in threads)
    assert all(t.kind == ThreadKind.INLINE for t in threads)


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_general_threads_wraps_comments(
        gitea_vcs_client: GiteaVCSClient,
):
    threads = await gitea_vcs_client.get_general_threads()
    assert all(isinstance(t, ReviewThreadSchema) for t in threads)
    assert all(t.kind == ThreadKind.SUMMARY for t in threads)
