import pytest

from ai_review.services.vcs.azure_devops.client import AzureDevOpsVCSClient
from ai_review.services.vcs.types import (
    ThreadKind,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)
from ai_review.tests.fixtures.clients.azure_devops import FakeAzureDevOpsPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_review_info_returns_valid_schema(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should return detailed PR info with author, reviewers, and changed files."""
    info = await azure_devops_vcs_client.get_review_info()

    assert isinstance(info, ReviewInfoSchema)
    assert info.id == 5
    assert info.title == "Test PR"
    assert info.description == "Fake Azure DevOps PR"

    assert info.author.name == "Author"
    assert info.author.username == "author@example.com"
    assert len(info.reviewers) == 1
    assert info.reviewers[0].username == "reviewer@example.com"

    assert info.source_branch.ref == "refs/heads/feature/test"
    assert info.target_branch.ref == "refs/heads/main"
    assert "src/app.py" in info.changed_files
    assert len(info.changed_files) == 2

    called_methods = [name for name, _ in fake_azure_devops_pull_requests_http_client.calls]
    assert called_methods == ["get_pull_request", "get_files"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_general_comments_returns_expected_list(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should return only general (non-inline) comments."""
    comments = await azure_devops_vcs_client.get_general_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 1
    assert comments[0].body == "General comment"
    assert comments[0].file is None

    called_methods = [name for name, _ in fake_azure_devops_pull_requests_http_client.calls]
    assert "get_threads" in called_methods


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_inline_comments_returns_expected_list(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should return inline comments with file and line context."""
    comments = await azure_devops_vcs_client.get_inline_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 1
    assert comments[0].file == "src/app.py"
    assert comments[0].body == "Inline comment"
    assert comments[0].thread_id == 1

    called_methods = [name for name, _ in fake_azure_devops_pull_requests_http_client.calls]
    assert "get_threads" in called_methods


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_create_general_comment_posts_comment(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should send a general comment using create_thread."""
    message = "Hello from Azure DevOps test!"
    await azure_devops_vcs_client.create_general_comment(message)

    calls = [args for name, args in fake_azure_devops_pull_requests_http_client.calls if name == "create_thread"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["pull_request_id"] == 5
    assert call_args["request"].comments[0].content == message
    assert call_args["request"].thread_context is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_create_inline_comment_posts_comment_with_context(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should create inline comment with proper thread context."""
    await azure_devops_vcs_client.create_inline_comment("src/app.py", 10, "Looks good!")

    calls = [args for name, args in fake_azure_devops_pull_requests_http_client.calls if name == "create_thread"]
    assert len(calls) == 1

    call_args = calls[0]
    request = call_args["request"]
    assert request.thread_context.file_path == "src/app.py"
    assert request.thread_context.right_file_start.line == 10
    assert request.comments[0].content == "Looks good!"


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_create_inline_reply_posts_comment(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should post reply to existing inline thread."""
    thread_id = 1
    message = "Agree with this change."

    await azure_devops_vcs_client.create_inline_reply(thread_id, message)

    calls = [args for name, args in fake_azure_devops_pull_requests_http_client.calls if name == "create_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["thread_id"] == thread_id
    assert call_args["request"].content == message


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_create_summary_reply_reuses_general_comment_method(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should call create_general_comment internally."""
    await azure_devops_vcs_client.create_summary_reply(99, "Thanks for update")

    calls = [name for name, _ in fake_azure_devops_pull_requests_http_client.calls]
    assert "create_thread" in calls


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_inline_threads_returns_grouped_threads(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should map inline threads into ReviewThreadSchema list."""
    threads = await azure_devops_vcs_client.get_inline_threads()

    assert all(isinstance(t, ReviewThreadSchema) for t in threads)
    assert len(threads) == 1

    first = threads[0]
    assert first.kind == ThreadKind.INLINE
    assert first.file == "src/app.py"
    assert isinstance(first.comments[0], ReviewCommentSchema)
    assert first.comments[0].body == "Inline comment"

    called_methods = [name for name, _ in fake_azure_devops_pull_requests_http_client.calls]
    assert "get_threads" in called_methods


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_general_threads_wraps_comments_in_threads(
        azure_devops_vcs_client: AzureDevOpsVCSClient,
        fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
):
    """Should wrap general comments as SUMMARY threads."""
    threads = await azure_devops_vcs_client.get_general_threads()

    assert all(isinstance(t, ReviewThreadSchema) for t in threads)
    assert all(t.kind == ThreadKind.SUMMARY for t in threads)
    assert len(threads) == 1

    comment = threads[0].comments[0]
    assert isinstance(comment, ReviewCommentSchema)
    assert comment.body == "General comment"
    assert comment.author.username == "user@example.com"

    called_methods = [name for name, _ in fake_azure_devops_pull_requests_http_client.calls]
    assert "get_threads" in called_methods


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_review_info_handles_exception_gracefully(
        monkeypatch: pytest.MonkeyPatch,
        azure_devops_vcs_client: AzureDevOpsVCSClient,
):
    async def broken_get_pull_request(*args, **kwargs):
        raise RuntimeError("network error")

    monkeypatch.setattr(
        azure_devops_vcs_client.http_client.pr,
        "get_pull_request",
        broken_get_pull_request,
    )

    result = await azure_devops_vcs_client.get_review_info()
    assert isinstance(result, ReviewInfoSchema)
    assert result.id is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_general_comments_handles_exception(
        monkeypatch: pytest.MonkeyPatch,
        azure_devops_vcs_client: AzureDevOpsVCSClient,
):
    async def broken_get_threads(*args, **kwargs):
        raise ValueError("oops")

    monkeypatch.setattr(
        azure_devops_vcs_client.http_client.pr,
        "get_threads",
        broken_get_threads,
    )

    comments = await azure_devops_vcs_client.get_general_comments()
    assert comments == []
