import pytest

from ai_review.services.vcs.gitlab.client import GitLabVCSClient
from ai_review.services.vcs.types import (
    ReviewInfoSchema,
    ReviewCommentSchema,
    ReviewThreadSchema,
    ThreadKind,
    SupportsBatchedComments,
)
from ai_review.tests.fixtures.clients.gitlab import FakeGitLabMergeRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_review_info_returns_valid_schema(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should return valid MR info with author, branches and changed files."""
    info = await gitlab_vcs_client.get_review_info()

    assert isinstance(info, ReviewInfoSchema)
    assert info.id == 1
    assert info.title == "Fake Merge Request"
    assert info.description == "This is a fake MR for testing"

    assert info.author.username == "tester"
    assert info.author.name == "Tester"
    assert info.author.id == 42

    assert info.source_branch.ref == "feature/test"
    assert info.target_branch.ref == "main"
    assert info.base_sha == "abc123"
    assert info.head_sha == "def456"
    assert info.start_sha == "ghi789"

    assert len(info.changed_files) == 1
    assert info.changed_files[0] == "main.py"

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert called_methods == ["get_changes"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_general_comments_returns_expected_list(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should return general MR-level notes."""
    comments = await gitlab_vcs_client.get_general_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 2

    bodies = [c.body for c in comments]
    assert "General comment" in bodies
    assert "Another note" in bodies

    authors = {comment.author.username for comment in comments}
    assert authors == {"charlie", "diana"}

    for comment in comments:
        assert comment.thread_id == comment.id
        assert comment.author.id is not None
        assert comment.author.name != ""
        assert comment.author.username != ""

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert called_methods == ["get_notes"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_inline_comments_returns_expected_list(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should return inline comments from MR discussions (including ones without position)."""
    comments = await gitlab_vcs_client.get_inline_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 3

    first = comments[0]
    assert first.body == "Inline comment A"
    assert first.file == "src/app.py"
    assert first.line == 12

    last = comments[-1]
    assert last.file is None
    assert last.line is None

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert called_methods == ["get_discussions"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_general_comment_posts_comment(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should post a general note to MR."""
    message = "Hello, GitLab!"

    await gitlab_vcs_client.create_general_comment(message)

    calls = [
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "create_note"
    ]
    assert len(calls) == 1
    call_args = calls[0]

    assert call_args["body"] == message
    assert call_args["project_id"] == "project-id"
    assert call_args["merge_request_id"] == "merge-request-id"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_inline_comment_posts_comment(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should create an inline discussion at specific file and line."""
    await gitlab_vcs_client.create_inline_comment("main.py", 5, "Looks good!")

    called_names = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert "get_changes" in called_names
    assert "create_discussion" in called_names

    calls = [
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "create_discussion"
    ]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["body"] == "Looks good!"
    assert call_args["project_id"] == "project-id"
    assert call_args["merge_request_id"] == "merge-request-id"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_inline_reply_posts_comment(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should reply to an existing inline discussion."""
    thread_id = "discussion-1"
    message = "I agree with this point."

    await gitlab_vcs_client.create_inline_reply(thread_id, message)

    call = next(
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "create_discussion_reply"
    )

    assert call["discussion_id"] == thread_id
    assert call["body"] == message
    assert call["project_id"] == "project-id"
    assert call["merge_request_id"] == "merge-request-id"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_summary_reply_uses_general_comment_method(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should reuse create_general_comment when replying to summary thread."""
    thread_id = "summary-1"
    message = "Thanks for clarifying."

    await gitlab_vcs_client.create_summary_reply(thread_id, message)

    call = next(
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "create_note"
    )

    assert call["body"] == message
    assert call["project_id"] == "project-id"
    assert call["merge_request_id"] == "merge-request-id"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_inline_threads_returns_valid_schema(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should transform GitLab discussions into inline threads, including those without position."""
    threads = await gitlab_vcs_client.get_inline_threads()

    assert all(isinstance(thread, ReviewThreadSchema) for thread in threads)
    assert len(threads) == 2

    first_thread = threads[0]
    assert first_thread.id == "discussion-1"
    assert first_thread.kind == ThreadKind.INLINE
    assert first_thread.file == "src/app.py"
    assert first_thread.line == 12
    assert len(first_thread.comments) == 2
    assert isinstance(first_thread.comments[0], ReviewCommentSchema)

    second_thread = threads[1]
    assert second_thread.id == "discussion-2"
    assert second_thread.file is None
    assert second_thread.line is None
    assert len(second_thread.comments) == 1

    called = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert "get_discussions" in called


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_general_threads_wraps_comments_in_threads(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should wrap each general MR note into its own SUMMARY thread."""
    threads = await gitlab_vcs_client.get_general_threads()

    assert len(threads) == 2
    for thread in threads:
        assert isinstance(thread, ReviewThreadSchema)
        assert thread.kind == ThreadKind.SUMMARY
        assert len(thread.comments) == 1
        assert isinstance(thread.comments[0], ReviewCommentSchema)

    called = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert "get_notes" in called


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_delete_general_comment_calls_delete_note(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should delete a general MR-level comment by note id."""
    comment_id = 123

    await gitlab_vcs_client.delete_general_comment(comment_id)

    calls = [
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "delete_note"
    ]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["note_id"] == str(comment_id)
    assert call_args["project_id"] == "project-id"
    assert call_args["merge_request_id"] == "merge-request-id"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_delete_inline_comment_calls_delete_discussion(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should delete an inline discussion by discussion id."""
    note_id = "discussion-42"

    await gitlab_vcs_client.delete_inline_comment(note_id)

    calls = [
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "delete_note"
    ]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["note_id"] == str(note_id)
    assert call_args["project_id"] == "project-id"
    assert call_args["merge_request_id"] == "merge-request-id"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_batch_http_client_config")
async def test_create_inline_comment_creates_draft_note_when_batching(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should create a draft note instead of a discussion when batch_comments is enabled."""
    await gitlab_vcs_client.create_inline_comment(file="src/app.py", line=12, message="Batched comment")

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert "create_draft_note" in called_methods
    assert "create_discussion" not in called_methods

    calls = [
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "create_draft_note"
    ]
    assert len(calls) == 1
    call_args = calls[0]

    assert call_args["note"] == "Batched comment"
    assert call_args["project_id"] == "project-id"
    assert call_args["merge_request_id"] == "merge-request-id"
    assert call_args["position"].new_path == "src/app.py"
    assert call_args["position"].new_line == 12
    assert gitlab_vcs_client.pending_comments == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_inline_comment_creates_discussion_by_default(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should keep posting discussions when batch_comments is disabled (default)."""
    await gitlab_vcs_client.create_inline_comment(file="src/app.py", line=12, message="Immediate comment")

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert "create_discussion" in called_methods
    assert "create_draft_note" not in called_methods
    assert gitlab_vcs_client.pending_comments == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_batch_http_client_config")
async def test_publish_comments_bulk_publishes_pending_drafts(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should bulk publish once pending draft notes exist and reset the counter."""
    await gitlab_vcs_client.create_inline_comment(file="src/app.py", line=12, message="Comment A")
    await gitlab_vcs_client.create_inline_comment(file="src/app.py", line=14, message="Comment B")

    await gitlab_vcs_client.publish_comments()

    calls = [
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "bulk_publish_draft_notes"
    ]
    assert len(calls) == 1
    assert calls[0]["project_id"] == "project-id"
    assert calls[0]["merge_request_id"] == "merge-request-id"
    assert gitlab_vcs_client.pending_comments == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_batch_http_client_config")
async def test_publish_comments_noop_without_pending_drafts(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should not call the API when no draft notes were created."""
    await gitlab_vcs_client.publish_comments()

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert called_methods == []


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_publish_comments_noop_when_batching_disabled(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should not call the API when batch_comments is disabled."""
    await gitlab_vcs_client.publish_comments()

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert called_methods == []


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_batch_http_client_config")
async def test_create_general_comment_creates_draft_note_when_batching(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should create a positionless draft note instead of a note when batch_comments is enabled."""
    await gitlab_vcs_client.create_general_comment("Batched summary")

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert "create_draft_note" in called_methods
    assert "create_note" not in called_methods

    calls = [
        args for name, args in fake_gitlab_merge_requests_http_client.calls
        if name == "create_draft_note"
    ]
    assert len(calls) == 1
    assert calls[0]["note"] == "Batched summary"
    assert calls[0]["position"] is None
    assert gitlab_vcs_client.pending_comments == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_batch_http_client_config")
async def test_publish_comments_covers_inline_and_general_drafts(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should count inline and general drafts together and bulk publish once."""
    await gitlab_vcs_client.create_inline_comment(file="src/app.py", line=12, message="Inline")
    await gitlab_vcs_client.create_general_comment("Summary")
    assert gitlab_vcs_client.pending_comments == 2

    await gitlab_vcs_client.publish_comments()

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert called_methods.count("bulk_publish_draft_notes") == 1
    assert gitlab_vcs_client.pending_comments == 0


@pytest.mark.usefixtures("gitlab_http_client_config")
def test_gitlab_client_has_batching_capability(gitlab_vcs_client: GitLabVCSClient):
    """GitLabVCSClient should expose the optional SupportsBatchedComments capability."""
    assert isinstance(gitlab_vcs_client, SupportsBatchedComments)
