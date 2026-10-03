import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.azure_devops.pr.client import AzureDevOpsPullRequestsHTTPClient
from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsCreatePRCommentRequestSchema,
    AzureDevOpsCreatePRThreadRequestSchema,
)
from ai_review.config import settings
from ai_review.tests.fixtures.clients.azure_devops import FakeAzureDevOpsPullRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_pull_request_sends_request_and_parses_response(
    fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
) -> None:
    expected = await fake_azure_devops_pull_requests_http_client.get_pull_request(
        organization="org",
        project="proj",
        repository_id="repo",
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
        client = AzureDevOpsPullRequestsHTTPClient(client=http_client)
        result = await client.get_pull_request(
            organization="org",
            project="proj",
            repository_id="repo",
            pull_request_id=7,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/org/proj/_apis/git/repositories/repo/pullRequests/7"
    assert requests[0].url.params["api-version"] == settings.vcs.http_client.api_version


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_threads_sends_request_and_parses_response(
    fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
) -> None:
    expected = await fake_azure_devops_pull_requests_http_client.get_threads(
        organization="org",
        project="proj",
        repository_id="repo",
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
        client = AzureDevOpsPullRequestsHTTPClient(client=http_client)
        result = await client.get_threads(
            organization="org",
            project="proj",
            repository_id="repo",
            pull_request_id=7,
        )

    assert result.value == expected.value
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/org/proj/_apis/git/repositories/repo/pullRequests/7/threads"
    assert requests[0].url.params["api-version"] == settings.vcs.http_client.api_version


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_create_thread_sends_request_and_parses_response(
    fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
) -> None:
    comment = AzureDevOpsCreatePRThreadRequestSchema(
        status="active",
        comments=[AzureDevOpsCreatePRCommentRequestSchema(content="Hello")],
    )
    expected = await fake_azure_devops_pull_requests_http_client.create_thread(
        organization="org",
        project="proj",
        repository_id="repo",
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
        client = AzureDevOpsPullRequestsHTTPClient(client=http_client)
        result = await client.create_thread(
            organization="org",
            project="proj",
            repository_id="repo",
            pull_request_id=7,
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/org/proj/_apis/git/repositories/repo/pullRequests/7/threads"
    assert requests[0].url.params["api-version"] == settings.vcs.http_client.api_version
    assert json.loads(requests[0].content) == {"status": "active", "comments": [{"content": "Hello"}]}


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_delete_thread_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = AzureDevOpsPullRequestsHTTPClient(client=http_client)
        result = await client.delete_thread(
            organization="org",
            project="proj",
            repository_id="repo",
            pull_request_id=7,
            thread_id=4,
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "PATCH"
    assert requests[0].url.path == "/org/proj/_apis/git/repositories/repo/pullRequests/7/threads/4"
    assert requests[0].url.params["api-version"] == settings.vcs.http_client.api_version
    assert json.loads(requests[0].content) == {"status": "closed"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_create_comment_sends_request_and_parses_response(
    fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
) -> None:
    comment = AzureDevOpsCreatePRCommentRequestSchema(content="Hello")
    expected = await fake_azure_devops_pull_requests_http_client.create_comment(
        organization="org",
        project="proj",
        repository_id="repo",
        pull_request_id=7,
        thread_id=4,
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
        client = AzureDevOpsPullRequestsHTTPClient(client=http_client)
        result = await client.create_comment(
            organization="org",
            project="proj",
            repository_id="repo",
            pull_request_id=7,
            thread_id=4,
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/org/proj/_apis/git/repositories/repo/pullRequests/7/threads/4/comments"
    assert requests[0].url.params["api-version"] == settings.vcs.http_client.api_version
    assert json.loads(requests[0].content) == {"content": "Hello"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_devops_http_client_config")
async def test_get_files_sends_request_and_parses_response(
    fake_azure_devops_pull_requests_http_client: FakeAzureDevOpsPullRequestsHTTPClient,
) -> None:
    expected = await fake_azure_devops_pull_requests_http_client.get_files(
        organization="org",
        project="proj",
        repository_id="repo",
        pull_request_id=7,
        iteration_id=2,
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = AzureDevOpsPullRequestsHTTPClient(client=http_client)
        result = await client.get_files(
            organization="org",
            project="proj",
            repository_id="repo",
            pull_request_id=7,
            iteration_id=2,
        )

    assert result.change_entries == expected.change_entries
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/org/proj/_apis/git/repositories/repo/pullRequests/7/iterations/2/changes"
    assert requests[0].url.params["api-version"] == settings.vcs.http_client.api_version
