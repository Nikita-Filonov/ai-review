import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.bitbucket_server.pr.client import BitbucketServerPullRequestsHTTPClient
from ai_review.clients.bitbucket_server.pr.schema.comments import BitbucketServerCreatePRCommentRequestSchema
from ai_review.config import settings
from ai_review.tests.fixtures.clients.bitbucket_server import FakeBitbucketServerPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_pull_request_sends_request_and_parses_response(
    fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
) -> None:
    expected = await fake_bitbucket_server_pull_requests_http_client.get_pull_request(
        project_key="PRJ",
        repo_slug="repo",
        pull_request_id=7,
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = BitbucketServerPullRequestsHTTPClient(client=http_client)
        result = await client.get_pull_request(
            project_key="PRJ",
            repo_slug="repo",
            pull_request_id=7,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/projects/PRJ/repos/repo/pull-requests/7"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_changes_sends_request_and_parses_response(
    fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
) -> None:
    expected = await fake_bitbucket_server_pull_requests_http_client.get_changes(
        project_key="PRJ",
        repo_slug="repo",
        pull_request_id=7,
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = BitbucketServerPullRequestsHTTPClient(client=http_client)
        result = await client.get_changes(
            project_key="PRJ",
            repo_slug="repo",
            pull_request_id=7,
        )

    assert result.values == expected.values
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/projects/PRJ/repos/repo/pull-requests/7/changes"
    assert dict(requests[0].url.params) == {"start": "0", "limit": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_activities_sends_request_and_parses_response(
    fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
) -> None:
    expected = await fake_bitbucket_server_pull_requests_http_client.get_activities(
        project_key="PRJ",
        repo_slug="repo",
        pull_request_id=7,
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = BitbucketServerPullRequestsHTTPClient(client=http_client)
        result = await client.get_activities(
            project_key="PRJ",
            repo_slug="repo",
            pull_request_id=7,
        )

    assert result.values == expected.values
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/projects/PRJ/repos/repo/pull-requests/7/activities"
    assert dict(requests[0].url.params) == {"start": "0", "limit": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_comment_sends_request_and_parses_response(
    fake_bitbucket_server_pull_requests_http_client: FakeBitbucketServerPullRequestsHTTPClient,
) -> None:
    comment = BitbucketServerCreatePRCommentRequestSchema(text="Hello")
    expected = await fake_bitbucket_server_pull_requests_http_client.create_comment(
        project_key="PRJ",
        repo_slug="repo",
        pull_request_id=7,
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
        client = BitbucketServerPullRequestsHTTPClient(client=http_client)
        result = await client.create_comment(
            project_key="PRJ",
            repo_slug="repo",
            pull_request_id=7,
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/projects/PRJ/repos/repo/pull-requests/7/comments"
    assert json.loads(requests[0].content) == {"text": "Hello"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_delete_comment_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = BitbucketServerPullRequestsHTTPClient(client=http_client)
        result = await client.delete_comment(
            project_key="PRJ",
            repo_slug="repo",
            pull_request_id=7,
            comment_id="3",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/projects/PRJ/repos/repo/pull-requests/7/comments/3"
