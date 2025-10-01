import pytest

from ai_review.services.vcs.github.client import GitHubVCSClient
from ai_review.services.vcs.types import ReviewInfoSchema, ReviewCommentSchema
from ai_review.tests.fixtures.clients.github import FakeGitHubPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_get_review_info_returns_valid_schema(
        github_vcs_client: GitHubVCSClient,
        fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
):
    """Should return detailed PR info with branches, author, and files."""
    info = await github_vcs_client.get_review_info()

    assert isinstance(info, ReviewInfoSchema)
    assert info.id == 1
    assert info.title == "Fake Pull Request"
    assert info.description == "This is a fake PR for testing"

    assert info.author.username == "tester"
    assert {a.username for a in info.assignees} == {"dev1", "dev2"}
    assert {r.username for r in info.reviewers} == {"reviewer"}

    assert info.source_branch.ref == "feature/test"
    assert info.target_branch.ref == "main"
    assert info.base_sha == "abc123"
    assert info.head_sha == "def456"

    assert "app/main.py" in info.changed_files
    assert len(info.changed_files) == 2

    called_methods = [name for name, _ in fake_github_pull_requests_http_client.calls]
    assert called_methods == ["get_pull_request", "get_files"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_get_general_comments_returns_expected_list(
        github_vcs_client: GitHubVCSClient,
        fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
):
    """Should return general (issue-level) comments."""
    comments = await github_vcs_client.get_general_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 2

    bodies = [c.body for c in comments]
    assert "General comment" in bodies
    assert "Another general comment" in bodies

    called_methods = [name for name, _ in fake_github_pull_requests_http_client.calls]
    assert called_methods == ["get_issue_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_get_inline_comments_returns_expected_list(
        github_vcs_client: GitHubVCSClient,
        fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
):
    """Should return inline comments with file and line references."""
    comments = await github_vcs_client.get_inline_comments()

    assert all(isinstance(c, ReviewCommentSchema) for c in comments)
    assert len(comments) == 2

    first = comments[0]
    assert first.body == "Inline comment"
    assert first.file == "file.py"
    assert first.line == 5

    called_methods = [name for name, _ in fake_github_pull_requests_http_client.calls]
    assert called_methods == ["get_review_comments"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_create_general_comment_posts_comment(
        github_vcs_client: GitHubVCSClient,
        fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
):
    """Should post a general (non-inline) comment."""
    message = "Hello from test!"

    await github_vcs_client.create_general_comment(message)

    calls = [args for name, args in fake_github_pull_requests_http_client.calls if name == "create_issue_comment"]
    assert len(calls) == 1
    call_args = calls[0]
    assert call_args["body"] == message
    assert call_args["repo"] == "repo"
    assert call_args["owner"] == "owner"


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_create_inline_comment_posts_comment(
        github_vcs_client: GitHubVCSClient,
        fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
):
    """Should post an inline comment with correct path, line and commit_id."""
    await github_vcs_client.create_inline_comment("file.py", 10, "Looks good")

    calls = [args for name, args in fake_github_pull_requests_http_client.calls if name == "create_review_comment"]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["path"] == "file.py"
    assert call_args["line"] == 10
    assert call_args["body"] == "Looks good"
    assert call_args["commit_id"] == "def456"  # from fake PR head
