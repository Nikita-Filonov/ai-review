import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.gitea.pr.client import GiteaPullRequestsHTTPClient
from ai_review.clients.gitea.pr.schema.comments import GiteaCreateCommentRequestSchema
from ai_review.clients.gitea.pr.schema.reviews import GiteaCreateReviewRequestSchema
from ai_review.config import settings
from ai_review.tests.fixtures.clients.gitea import FakeGiteaPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_pull_request_sends_request_and_parses_response(
    fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
) -> None:
    expected = await fake_gitea_pull_requests_http_client.get_pull_request(
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
        client = GiteaPullRequestsHTTPClient(client=http_client)
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
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_files_sends_request_and_parses_response(
    fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
) -> None:
    expected = await fake_gitea_pull_requests_http_client.get_files(
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
        client = GiteaPullRequestsHTTPClient(client=http_client)
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
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_comments_sends_request_and_parses_response(
    fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
) -> None:
    expected = await fake_gitea_pull_requests_http_client.get_comments(
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
        client = GiteaPullRequestsHTTPClient(client=http_client)
        result = await client.get_comments(
            owner="owner",
            repo="repo",
            pull_number="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repos/owner/repo/issues/7/comments"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_create_comment_sends_request_and_parses_response(
    fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
) -> None:
    comment = GiteaCreateCommentRequestSchema(body="Hello")
    expected = await fake_gitea_pull_requests_http_client.create_comment(
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
        client = GiteaPullRequestsHTTPClient(client=http_client)
        result = await client.create_comment(
            owner="owner",
            repo="repo",
            pull_number="7",
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/repos/owner/repo/issues/7/comments"
    assert json.loads(requests[0].content) == {"body": "Hello"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_create_review_sends_request_and_parses_response(
    fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
) -> None:
    comment = GiteaCreateReviewRequestSchema(body="Hello", event="COMMENT", comments=[], commit_id=None)
    expected = await fake_gitea_pull_requests_http_client.create_review(
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
        client = GiteaPullRequestsHTTPClient(client=http_client)
        result = await client.create_review(
            owner="owner",
            repo="repo",
            pull_number="7",
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/reviews"
    assert json.loads(requests[0].content) == {
        "body": "Hello",
        "event": "COMMENT",
        "comments": [],
        "commit_id": None,
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_reviews_sends_request_and_parses_response(
    fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
) -> None:
    expected = await fake_gitea_pull_requests_http_client.get_reviews(
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
        client = GiteaPullRequestsHTTPClient(client=http_client)
        result = await client.get_reviews(
            owner="owner",
            repo="repo",
            pull_number="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/reviews"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_get_review_comments_sends_request_and_parses_response(
    fake_gitea_pull_requests_http_client: FakeGiteaPullRequestsHTTPClient,
) -> None:
    expected = await fake_gitea_pull_requests_http_client.get_review_comments(
        owner="owner",
        repo="repo",
        pull_number="7",
        review_id=4,
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GiteaPullRequestsHTTPClient(client=http_client)
        result = await client.get_review_comments(
            owner="owner",
            repo="repo",
            pull_number="7",
            review_id=4,
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/reviews/4/comments"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_delete_review_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GiteaPullRequestsHTTPClient(client=http_client)
        result = await client.delete_review(
            owner="owner",
            repo="repo",
            pull_number="7",
            review_id=4,
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/repos/owner/repo/pulls/7/reviews/4"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_delete_issue_comment_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GiteaPullRequestsHTTPClient(client=http_client)
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
@pytest.mark.usefixtures("gitea_http_client_config")
async def test_delete_review_comment_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GiteaPullRequestsHTTPClient(client=http_client)
        result = await client.delete_review_comment(
            owner="owner",
            repo="repo",
            comment_id="3",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/repos/owner/repo/pulls/comments/3"
