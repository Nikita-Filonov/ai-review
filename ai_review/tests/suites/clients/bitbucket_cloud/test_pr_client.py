import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.bitbucket_cloud.pr.client import BitbucketCloudPullRequestsHTTPClient
from ai_review.clients.bitbucket_cloud.pr.schema.comments import (
    BitbucketCloudCommentContentSchema,
    BitbucketCloudCreatePRCommentRequestSchema,
)
from ai_review.config import settings
from ai_review.tests.fixtures.clients.bitbucket_cloud import FakeBitbucketCloudPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_pull_request_sends_request_and_parses_response(
    fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
) -> None:
    expected = await fake_bitbucket_cloud_pull_requests_http_client.get_pull_request(
        workspace="workspace",
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
        client = BitbucketCloudPullRequestsHTTPClient(client=http_client)
        result = await client.get_pull_request(
            workspace="workspace",
            repo_slug="repo",
            pull_request_id=7,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repositories/workspace/repo/pullrequests/7"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_files_sends_request_and_parses_response(
    fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
) -> None:
    expected = await fake_bitbucket_cloud_pull_requests_http_client.get_files(
        workspace="workspace",
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
        client = BitbucketCloudPullRequestsHTTPClient(client=http_client)
        result = await client.get_files(
            workspace="workspace",
            repo_slug="repo",
            pull_request_id=7,
        )

    assert result.values == expected.values
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repositories/workspace/repo/pullrequests/7/diffstat"
    assert dict(requests[0].url.params) == {"page": "1", "pagelen": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_get_comments_sends_request_and_parses_response(
    fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
) -> None:
    expected = await fake_bitbucket_cloud_pull_requests_http_client.get_comments(
        workspace="workspace",
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
        client = BitbucketCloudPullRequestsHTTPClient(client=http_client)
        result = await client.get_comments(
            workspace="workspace",
            repo_slug="repo",
            pull_request_id=7,
        )

    assert result.values == expected.values
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/repositories/workspace/repo/pullrequests/7/comments"
    assert dict(requests[0].url.params) == {"page": "1", "pagelen": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_create_comment_sends_request_and_parses_response(
    fake_bitbucket_cloud_pull_requests_http_client: FakeBitbucketCloudPullRequestsHTTPClient,
) -> None:
    comment = BitbucketCloudCreatePRCommentRequestSchema(
        content=BitbucketCloudCommentContentSchema(raw="Hello")
    )
    expected = await fake_bitbucket_cloud_pull_requests_http_client.create_comment(
        workspace="workspace",
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
        client = BitbucketCloudPullRequestsHTTPClient(client=http_client)
        result = await client.create_comment(
            workspace="workspace",
            repo_slug="repo",
            pull_request_id=7,
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/repositories/workspace/repo/pullrequests/7/comments"
    assert json.loads(requests[0].content) == {"content": {"raw": "Hello"}}


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
async def test_delete_comment_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = BitbucketCloudPullRequestsHTTPClient(client=http_client)
        result = await client.delete_comment(
            workspace="workspace",
            repo_slug="repo",
            pull_request_id=7,
            comment_id="3",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "PUT"
    assert requests[0].url.path == "/repositories/workspace/repo/pullrequests/7/comments/3"
    assert json.loads(requests[0].content) == {"content": {"raw": "*(comment removed by ai-review)*"}}
