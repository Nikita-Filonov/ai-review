import pytest

from ai_review.services.vcs.gitlab.client import GitLabVCSClient
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewCommentSchema
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

    called_methods = [name for name, _ in fake_gitlab_merge_requests_http_client.calls]
    assert called_methods == ["get_notes"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_inline_comments_returns_expected_list(
        gitlab_vcs_client: GitLabVCSClient,
        fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
):
    """Should return inline comments from MR discussions."""
    comments = await gitlab_vcs_client.get_inline_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 2

    first = comments[0]
    assert first.body == "Inline comment A"

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
