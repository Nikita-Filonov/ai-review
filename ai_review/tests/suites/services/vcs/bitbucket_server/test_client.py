import pytest

from ai_review.services.vcs.bitbucket_server.client import BitbucketServerVCSClient
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewCommentSchema, ReviewThreadSchema, ThreadKind
from ai_review.tests.fixtures.clients.bitbucket_server import FakeBitbucketServerPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_review_info_returns_valid_schema(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should return detailed PR info with branches, author, reviewers, and files."""
    info = await bitbucket_server_vcs_client.get_review_info()

    assert isinstance(info, ReviewInfoSchema)
    assert info.id == 1
    assert info.title == "Fake Bitbucket Server PR"
    assert info.description == "PR for testing server client"

    assert info.author.username == "author"
    assert {reviewer.username for reviewer in info.reviewers} == {"reviewer"}

    assert info.source_branch.ref == "feature/test"
    assert info.target_branch.ref == "main"
    assert info.base_sha == "abc123"
    assert info.head_sha == "def456"

    assert "src/main.py" in info.changed_files
    assert len(info.changed_files) == 1

    called_methods = [name for name, _ in fake_bitbucket_server_pull_requests_http_client.calls]
    assert called_methods == ["get_pull_request", "get_changes"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_general_comments_filters_inline(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should return only general comments (without anchor)."""
    comments = await bitbucket_server_vcs_client.get_general_comments()

    assert all(isinstance(comment, ReviewCommentSchema) for comment in comments)
    assert len(comments) == 1

    first = comments[0]
    assert first.body == "General comment"
    assert first.file is None
    assert first.line is None

    called_methods = [name for name, _ in fake_bitbucket_server_pull_requests_http_client.calls]
    assert called_methods == ["get_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_inline_comments_filters_general(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should return only inline comments with file and line references."""
    comments = await bitbucket_server_vcs_client.get_inline_comments()

    assert all(isinstance(comment, ReviewCommentSchema) for comment in comments)
    assert len(comments) == 1

    first = comments[0]
    assert first.body == "Inline comment"
    assert first.file == "src/main.py"
    assert first.line == 5

    called_methods = [name for name, _ in fake_bitbucket_server_pull_requests_http_client.calls]
    assert called_methods == ["get_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_general_comment_posts_comment(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should post a general (non-inline) comment."""
    message = "Hello from Bitbucket Server test!"

    await bitbucket_server_vcs_client.create_general_comment(message)

    calls = [args for name, args in fake_bitbucket_server_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1
    call_args = calls[0]
    assert call_args["text"] == message
    assert call_args["project_key"] == "PRJ"
    assert call_args["repo_slug"] == "repo"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_inline_comment_posts_comment(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should post an inline comment with correct file and line."""
    file = "src/app.py"
    line = 10
    message = "Looks good"

    await bitbucket_server_vcs_client.create_inline_comment(file, line, message)

    calls = [args for name, args in fake_bitbucket_server_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["text"] == message
    assert call_args["anchor"]["path"] == file
    assert call_args["anchor"]["line"] == line
    assert call_args["anchor"]["lineType"] == "ADDED"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_inline_reply_posts_comment(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should post a reply to an existing inline thread."""
    thread_id = 42
    message = "Reply inline comment"

    await bitbucket_server_vcs_client.create_inline_reply(thread_id, message)

    calls = [args for name, args in fake_bitbucket_server_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["parent"]["id"] == thread_id
    assert call_args["text"] == message


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_summary_reply_posts_comment(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should post a reply to a general thread (same API with parent id)."""
    thread_id = 7
    message = "Thanks for the clarification."

    await bitbucket_server_vcs_client.create_summary_reply(thread_id, message)

    calls = [args for name, args in fake_bitbucket_server_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["parent"]["id"] == thread_id
    assert call_args["text"] == message


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_inline_threads_groups_by_thread_id(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should group inline comments into threads."""
    threads = await bitbucket_server_vcs_client.get_inline_threads()

    assert all(isinstance(thread, ReviewThreadSchema) for thread in threads)
    assert len(threads) == 1

    thread = threads[0]
    assert thread.kind == ThreadKind.INLINE
    assert thread.file == "src/main.py"
    assert thread.line == 5
    assert len(thread.comments) == 1
    assert isinstance(thread.comments[0], ReviewCommentSchema)

    called_methods = [name for name, _ in fake_bitbucket_server_pull_requests_http_client.calls]
    assert "get_comments" in called_methods


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_general_threads_groups_by_thread_id(
        bitbucket_server_vcs_client: BitbucketServerVCSClient,
        fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
):
    """Should group general (non-inline) comments into SUMMARY threads."""
    threads = await bitbucket_server_vcs_client.get_general_threads()

    assert all(isinstance(thread, ReviewThreadSchema) for thread in threads)
    assert len(threads) == 1
    thread = threads[0]
    assert thread.kind == ThreadKind.SUMMARY
    assert len(thread.comments) == 1
    assert isinstance(thread.comments[0], ReviewCommentSchema)

    called_methods = [name for name, _ in fake_bitbucket_server_pull_requests_http_client.calls]
    assert "get_comments" in called_methods
