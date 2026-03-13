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
    assert all(isinstance(comment, ReviewCommentSchema) for comment in comments)
    assert len(comments) > 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_inline_comments_returns_fallback_general_comments(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    comments = await gitea_vcs_client.get_inline_comments()
    assert isinstance(comments, list)
    assert all(isinstance(comment, ReviewCommentSchema) for comment in comments)
    assert len(comments) > 0


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
async def test_create_inline_comment_posts_review(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    await gitea_vcs_client.create_inline_comment(
        file="src/main.py",
        line=10,
        message="Inline comment",
    )

    calls = fake_gitea_pull_requests_http_client.calls

    assert any(name == "create_review" for name, _ in calls)
    assert not any(name == "create_comment" for name, _ in calls)


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_create_inline_comment_raises_on_error(
        monkeypatch: pytest.MonkeyPatch,
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    async def fail_create_review(*_, **__):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        fake_gitea_pull_requests_http_client,
        "create_review",
        fail_create_review,
    )

    with pytest.raises(RuntimeError):
        await gitea_vcs_client.create_inline_comment(
            file="src/main.py",
            line=10,
            message="Inline comment",
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_inline_threads_groups_by_comment(
        gitea_vcs_client: GiteaVCSClient,
):
    threads = await gitea_vcs_client.get_inline_threads()
    assert all(isinstance(thread, ReviewThreadSchema) for thread in threads)
    assert all(thread.kind == ThreadKind.INLINE for thread in threads)


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_general_threads_wraps_comments(
        gitea_vcs_client: GiteaVCSClient,
):
    threads = await gitea_vcs_client.get_general_threads()
    assert all(isinstance(thread, ReviewThreadSchema) for thread in threads)
    assert all(thread.kind == ThreadKind.SUMMARY for thread in threads)


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_delete_general_comment_calls_delete_issue_comment(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    """Should delete a general PR comment by id."""
    comment_id = 123

    await gitea_vcs_client.delete_general_comment(comment_id)

    calls = [
        args for name, args in fake_gitea_pull_requests_http_client.calls
        if name == "delete_issue_comment"
    ]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["comment_id"] == comment_id
    assert call_args["owner"] == "owner"
    assert call_args["repo"] == "repo"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_delete_inline_comment_calls_delete_review_comment(
        gitea_vcs_client: GiteaVCSClient,
        fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
):
    """Should delete an inline review comment by id."""
    comment_id = "review-42"

    await gitea_vcs_client.delete_inline_comment(comment_id)

    calls = [
        args for name, args in fake_gitea_pull_requests_http_client.calls
        if name == "delete_review_comment"
    ]
    assert len(calls) == 1

    call_args = calls[0]
    assert call_args["comment_id"] == comment_id
    assert call_args["owner"] == "owner"
    assert call_args["repo"] == "repo"
