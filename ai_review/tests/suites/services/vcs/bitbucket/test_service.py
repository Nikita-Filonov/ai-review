import pytest

from ai_review.services.vcs.bitbucket.client import BitbucketVCSClient
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewCommentSchema
from ai_review.tests.fixtures.clients.bitbucket import FakeBitbucketPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_http_client_config")
async def test_get_review_info_returns_valid_schema(
        bitbucket_vcs_client: BitbucketVCSClient,
        fake_bitbucket_pull_requests_http_client: FakeBitbucketPullRequestsHTTPClient,
):
    """Should return detailed PR info with branches, author, reviewers, and files."""
    info = await bitbucket_vcs_client.get_review_info()

    assert isinstance(info, ReviewInfoSchema)
    assert info.id == 1
    assert info.title == "Fake Bitbucket PR"
    assert info.description == "This is a fake PR for testing"

    assert info.author.username == "tester"
    assert {r.username for r in info.reviewers} == {"reviewer"}

    assert info.source_branch.ref == "feature/test"
    assert info.target_branch.ref == "main"
    assert info.base_sha == "abc123"
    assert info.head_sha == "def456"

    assert "app/main.py" in info.changed_files
    assert len(info.changed_files) == 2

    called_methods = [name for name, _ in fake_bitbucket_pull_requests_http_client.calls]
    assert called_methods == ["get_pull_request", "get_files"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_http_client_config")
async def test_get_general_comments_filters_inline(
        bitbucket_vcs_client: BitbucketVCSClient,
        fake_bitbucket_pull_requests_http_client: FakeBitbucketPullRequestsHTTPClient,
):
    """Should return only general comments (without inline info)."""
    comments = await bitbucket_vcs_client.get_general_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 1

    first = comments[0]
    assert first.body == "General comment"
    assert first.file is None
    assert first.line is None

    called_methods = [name for name, _ in fake_bitbucket_pull_requests_http_client.calls]
    assert called_methods == ["get_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_http_client_config")
async def test_get_inline_comments_filters_general(
        bitbucket_vcs_client: BitbucketVCSClient,
        fake_bitbucket_pull_requests_http_client: FakeBitbucketPullRequestsHTTPClient,
):
    """Should return only inline comments with file and line references."""
    comments = await bitbucket_vcs_client.get_inline_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 1

    first = comments[0]
    assert first.body == "Inline comment"
    assert first.file == "file.py"
    assert first.line == 5

    called_methods = [name for name, _ in fake_bitbucket_pull_requests_http_client.calls]
    assert called_methods == ["get_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_http_client_config")
async def test_create_general_comment_posts_comment(
        bitbucket_vcs_client: BitbucketVCSClient,
        fake_bitbucket_pull_requests_http_client: FakeBitbucketPullRequestsHTTPClient,
):
    """Should post a general (non-inline) comment."""
    message = "Hello from Bitbucket test!"

    await bitbucket_vcs_client.create_general_comment(message)

    calls = [args for name, args in fake_bitbucket_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1
    call_args = calls[0]
    assert call_args["content"]["raw"] == message
    assert call_args["workspace"] == "workspace"
    assert call_args["repo_slug"] == "repo"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_http_client_config")
async def test_create_inline_comment_posts_comment(
        bitbucket_vcs_client: BitbucketVCSClient,
        fake_bitbucket_pull_requests_http_client: FakeBitbucketPullRequestsHTTPClient,
):
    """Should post an inline comment with correct file and line."""
    file = "file.py"
    line = 10
    message = "Looks good"

    await bitbucket_vcs_client.create_inline_comment(file, line, message)

    calls = [args for name, args in fake_bitbucket_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["content"]["raw"] == message
    assert call_args["inline"]["path"] == file
    assert call_args["inline"]["to"] == line
