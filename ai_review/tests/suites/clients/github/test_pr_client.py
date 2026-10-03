import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.github.pr.client import GitHubPullRequestsHTTPClient, GitHubPullRequestsHTTPClientError
from ai_review.clients.github.pr.schema.comments import (
    GitHubCreateReviewCommentRequestSchema,
    GitHubCreateReviewReplyRequestSchema,
)
from ai_review.config import settings
from ai_review.tests.fixtures.clients.github import FakeGitHubPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_get_pull_request_sends_request_and_parses_response(
    fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
) -> None:
    expected = await fake_github_pull_requests_http_client.get_pull_request(
        owner="owner",
        repo="repo",
        pull_number="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.get_pull_request(
            owner="owner",
            repo="repo",
            pull_number="7",
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7"


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_get_files_sends_request_and_parses_response(
    fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
) -> None:
    expected = await fake_github_pull_requests_http_client.get_files(
        owner="owner",
        repo="repo",
        pull_number="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.get_files(
            owner="owner",
            repo="repo",
            pull_number="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/files"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_get_issue_comments_sends_request_and_parses_response(
    fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
) -> None:
    expected = await fake_github_pull_requests_http_client.get_issue_comments(
        owner="owner",
        repo="repo",
        issue_number="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.get_issue_comments(
            owner="owner",
            repo="repo",
            issue_number="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repos/owner/repo/issues/7/comments"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_get_review_comments_sends_request_and_parses_response(
    fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
) -> None:
    expected = await fake_github_pull_requests_http_client.get_review_comments(
        owner="owner",
        repo="repo",
        pull_number="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.get_review_comments(
            owner="owner",
            repo="repo",
            pull_number="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/comments"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_create_review_reply_sends_request_and_parses_response(
    fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
) -> None:
    comment = GitHubCreateReviewReplyRequestSchema(body="Hello", in_reply_to=4)
    expected = await fake_github_pull_requests_http_client.create_review_reply(
        owner="owner",
        repo="repo",
        pull_number="7",
        request=comment,
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(201, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.create_review_reply(
            owner="owner",
            repo="repo",
            pull_number="7",
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/comments"
    assert json.loads(requests[0].content) == {"body": "Hello", "in_reply_to": 4}


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_create_review_comment_sends_request_and_parses_response(
    fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
) -> None:
    comment = GitHubCreateReviewCommentRequestSchema(body="Hello", path="file.py", line=2, commit_id="abc")
    expected = await fake_github_pull_requests_http_client.create_review_comment(
        owner="owner",
        repo="repo",
        pull_number="7",
        request=comment,
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(201, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.create_review_comment(
            owner="owner",
            repo="repo",
            pull_number="7",
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/comments"
    assert json.loads(requests[0].content) == {
        "body": "Hello",
        "path": "file.py",
        "line": 2,
        "commit_id": "abc",
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_create_issue_comment_sends_request_and_parses_response(
    fake_github_pull_requests_http_client: FakeGitHubPullRequestsHTTPClient,
) -> None:
    expected = await fake_github_pull_requests_http_client.create_issue_comment(
        owner="owner",
        repo="repo",
        issue_number="7",
        body="Hello",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(201, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.create_issue_comment(
            owner="owner",
            repo="repo",
            issue_number="7",
            body="Hello",
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/repos/owner/repo/issues/7/comments"
    assert json.loads(requests[0].content) == {"body": "Hello"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_delete_review_comment_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.delete_review_comment(
            owner="owner",
            repo="repo",
            comment_id="3",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/repos/owner/repo/pulls/comments/3"


@pytest.mark.asyncio
@pytest.mark.usefixtures("github_http_client_config")
async def test_delete_issue_comment_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitHubPullRequestsHTTPClient(client=http_client)
        result = await client.delete_issue_comment(
            owner="owner",
            repo="repo",
            comment_id="3",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/repos/owner/repo/issues/comments/3"


@pytest.mark.asyncio
async def test_remote_http_error_preserves_status_and_message():
    async with AsyncClient(
        transport=MockTransport(lambda _: Response(403, text="Forbidden")),
        base_url="https://api.example.test",
    ) as http:
        client = GitHubPullRequestsHTTPClient(http)
        with pytest.raises(GitHubPullRequestsHTTPClientError) as error:
            await client.get_pull_request_api("owner", "repo", "7")

    assert error.value.status_code == 403
    assert "Forbidden" in error.value.details
