import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.gitlab.mr.client import GitLabMergeRequestsHTTPClient
from ai_review.clients.gitlab.mr.schema.discussions import GitLabCreateMRDiscussionRequestSchema
from ai_review.clients.gitlab.mr.schema.draft_notes import GitLabCreateMRDraftNoteRequestSchema
from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema
from ai_review.config import settings
from ai_review.tests.fixtures.clients.gitlab import FakeGitLabMergeRequestsHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_changes_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    expected = await fake_gitlab_merge_requests_http_client.get_changes(
        project_id="project",
        merge_request_id="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.get_changes(
            project_id="project",
            merge_request_id="7",
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/changes"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_notes_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    expected = await fake_gitlab_merge_requests_http_client.get_notes(
        project_id="project",
        merge_request_id="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.get_notes(
            project_id="project",
            merge_request_id="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/notes"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_discussions_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    expected = await fake_gitlab_merge_requests_http_client.get_discussions(
        project_id="project",
        merge_request_id="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.get_discussions(
            project_id="project",
            merge_request_id="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/discussions"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_note_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    expected = await fake_gitlab_merge_requests_http_client.create_note(
        body="Hello",
        project_id="project",
        merge_request_id="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(201, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.create_note(
            body="Hello",
            project_id="project",
            merge_request_id="7",
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/notes"
    assert json.loads(requests[0].content) == {"body": "Hello"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_discussion_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    comment = GitLabCreateMRDiscussionRequestSchema(
        body="Hello",
        position=GitLabPositionSchema(
            new_path="file.py", new_line=2, base_sha="base", head_sha="head", start_sha="start"
        ),
    )
    expected = await fake_gitlab_merge_requests_http_client.create_discussion(
        project_id="project",
        merge_request_id="7",
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
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.create_discussion(
            project_id="project",
            merge_request_id="7",
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/discussions"
    body = json.loads(requests[0].content)
    assert body["body"] == "Hello"
    assert body["position"]["new_path"] == "file.py"
    assert body["position"]["new_line"] == 2


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_discussion_reply_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    expected = await fake_gitlab_merge_requests_http_client.create_discussion_reply(
        project_id="project",
        merge_request_id="7",
        discussion_id="d",
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
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.create_discussion_reply(
            project_id="project",
            merge_request_id="7",
            discussion_id="d",
            body="Hello",
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/discussions/d/notes"
    assert json.loads(requests[0].content) == {"body": "Hello"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_delete_note_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.delete_note(
            project_id="project",
            merge_request_id="7",
            note_id="3",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/notes/3"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_create_draft_note_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    comment = GitLabCreateMRDraftNoteRequestSchema(note="Hello", position=None)
    expected = await fake_gitlab_merge_requests_http_client.create_draft_note(
        project_id="project",
        merge_request_id="7",
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
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.create_draft_note(
            project_id="project",
            merge_request_id="7",
            request=comment,
        )

    assert result == expected
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/draft_notes"
    assert json.loads(requests[0].content) == {"note": "Hello"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_get_draft_notes_sends_request_and_parses_response(
    fake_gitlab_merge_requests_http_client: FakeGitLabMergeRequestsHTTPClient,
) -> None:
    expected = await fake_gitlab_merge_requests_http_client.get_draft_notes(
        project_id="project",
        merge_request_id="7",
    )
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200, content=expected.model_dump_json(by_alias=True))

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.get_draft_notes(
            project_id="project",
            merge_request_id="7",
        )

    assert result.root == expected.root
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/draft_notes"
    assert dict(requests[0].url.params) == {"page": "1", "per_page": str(settings.vcs.pagination.per_page)}


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_delete_draft_note_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.delete_draft_note(
            project_id="project",
            merge_request_id="7",
            draft_note_id="5",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "DELETE"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/draft_notes/5"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gitlab_http_client_config")
async def test_bulk_publish_draft_notes_sends_expected_request() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(204)

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GitLabMergeRequestsHTTPClient(client=http_client)
        result = await client.bulk_publish_draft_notes(
            project_id="project",
            merge_request_id="7",
        )

    assert result is None
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/api/v4/projects/project/merge_requests/7/draft_notes/bulk_publish"
