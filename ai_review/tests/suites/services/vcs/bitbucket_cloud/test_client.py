import pytest

from ai_review.services.vcs.bitbucket_cloud.client import BitbucketCloudVCSClient
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewCommentSchema, ReviewThreadSchema, ThreadKind
from ai_review.tests.fixtures.clients.bitbucket_cloud import FakeBitbucketCloudPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_review_info_returns_valid_schema(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should return detailed PR info with branches, author, reviewers, and files."""
    info = await bitbucket_cloud_vcs_client.get_review_info()

    assert isinstance(info, ReviewInfoSchema)
    assert info.id == 1
    assert info.title == "Fake Bitbucket PR"
    assert info.description == "This is a fake PR for testing"

    assert info.author.username == "tester"
    assert {reviewer.username for reviewer in info.reviewers} == {"reviewer"}

    assert info.source_branch.ref == "feature/test"
    assert info.target_branch.ref == "main"
    assert info.base_sha == "abc123"
    assert info.head_sha == "def456"

    assert "app/main.py" in info.changed_files
    assert len(info.changed_files) == 2

    called_methods = [name for name, _ in fake_bitbucket_cloud_pull_requests_http_client.calls]
    assert called_methods == ["get_pull_request", "get_files"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_general_comments_filters_inline(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should return only general comments (without inline info)."""
    comments = await bitbucket_cloud_vcs_client.get_general_comments()

    assert all(isinstance(comment, ReviewCommentSchema) for comment in comments)
    assert len(comments) == 1

    first = comments[0]
    assert first.body == "General comment"
    assert first.file is None
    assert first.line is None

    called_methods = [name for name, _ in fake_bitbucket_cloud_pull_requests_http_client.calls]
    assert called_methods == ["get_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_inline_comments_filters_general(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should return only inline comments with file and line references."""
    comments = await bitbucket_cloud_vcs_client.get_inline_comments()

    assert all(isinstance(comment, ReviewCommentSchema) for comment in comments)
    assert len(comments) == 1

    first = comments[0]
    assert first.body == "Inline comment"
    assert first.file == "file.py"
    assert first.line == 5

    called_methods = [name for name, _ in fake_bitbucket_cloud_pull_requests_http_client.calls]
    assert called_methods == ["get_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_create_general_comment_posts_comment(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should post a general (non-inline) comment."""
    message = "Hello from Bitbucket test!"

    await bitbucket_cloud_vcs_client.create_general_comment(message)

    calls = [args for name, args in fake_bitbucket_cloud_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1
    call_args = calls[0]
    assert call_args["content"]["raw"] == message
    assert call_args["workspace"] == "workspace"
    assert call_args["repo_slug"] == "repo"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_create_inline_comment_posts_comment(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should post an inline comment with correct file and line."""
    file = "file.py"
    line = 10
    message = "Looks good"

    await bitbucket_cloud_vcs_client.create_inline_comment(file, line, message)

    calls = [args for name, args in fake_bitbucket_cloud_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["content"]["raw"] == message
    assert call_args["inline"]["path"] == file
    assert call_args["inline"]["to"] == line


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_create_inline_reply_posts_comment(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should post a reply to an existing inline thread."""
    thread_id = 42
    message = "I agree with this inline comment."

    await bitbucket_cloud_vcs_client.create_inline_reply(thread_id, message)

    calls = [args for name, args in fake_bitbucket_cloud_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["parent"]["id"] == thread_id
    assert call_args["content"]["raw"] == message
    assert call_args["workspace"] == "workspace"
    assert call_args["repo_slug"] == "repo"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_create_summary_reply_posts_comment_with_parent(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should post a reply to a general thread (same API with parent id)."""
    thread_id = 7
    message = "Thanks for the clarification."

    await bitbucket_cloud_vcs_client.create_summary_reply(thread_id, message)

    calls = [args for name, args in fake_bitbucket_cloud_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["parent"]["id"] == thread_id
    assert call_args["content"]["raw"] == message
    assert call_args["workspace"] == "workspace"
    assert call_args["repo_slug"] == "repo"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_inline_threads_groups_by_thread_id(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should group inline comments into threads."""
    threads = await bitbucket_cloud_vcs_client.get_inline_threads()

    assert all(isinstance(thread, ReviewThreadSchema) for thread in threads)
    assert len(threads) == 1

    thread = threads[0]
    assert thread.kind == ThreadKind.INLINE
    assert thread.file == "file.py"
    assert thread.line == 5
    assert len(thread.comments) == 1
    assert isinstance(thread.comments[0], ReviewCommentSchema)

    called_methods = [name for name, _ in fake_bitbucket_cloud_pull_requests_http_client.calls]
    assert "get_comments" in called_methods


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_general_threads_groups_by_thread_id(
        bitbucket_cloud_vcs_client: BitbucketCloudVCSClient,
        fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
):
    """Should group general (non-inline) comments into SUMMARY threads."""
    threads = await bitbucket_cloud_vcs_client.get_general_threads()

    assert all(isinstance(thread, ReviewThreadSchema) for thread in threads)
    assert len(threads) == 1
    thread = threads[0]
    assert thread.kind == ThreadKind.SUMMARY
    assert len(thread.comments) == 1
    assert isinstance(thread.comments[0], ReviewCommentSchema)

    called_methods = [name for name, _ in fake_bitbucket_cloud_pull_requests_http_client.calls]
    assert "get_comments" in called_methods
