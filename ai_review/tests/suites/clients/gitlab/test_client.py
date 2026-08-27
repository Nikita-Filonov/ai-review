import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from ai_review.clients.gitlab.client import get_gitlab_http_client, GitLabHTTPClient
from ai_review.clients.gitlab.mr.client import GitLabMergeRequestsHTTPClient
from ai_review.clients.gitlab.mr.schema.notes import GitLabCreateMRNoteRequestSchema
from ai_review.libs.http.transports.retry import NO_RETRY_EXTENSION


@pytest.mark.usefixtures("gitlab_http_client_config")
def test_get_gitlab_http_client_builds_ok():
    gitlab_http_client = get_gitlab_http_client()

    assert isinstance(gitlab_http_client, GitLabHTTPClient)
    assert isinstance(gitlab_http_client.mr, GitLabMergeRequestsHTTPClient)
    assert isinstance(gitlab_http_client.mr.client, AsyncClient)


@pytest.mark.asyncio
async def test_bulk_publish_draft_notes_api_opts_out_of_retries_unlike_other_endpoints() -> None:
    """The bulk-publish request must carry the retry opt-out; other endpoints must not.

    Every GitLab test elsewhere goes through the fake client and bypasses HTTP, so this
    is the only test that would fail if `extensions=NO_RETRY` were removed from
    `bulk_publish_draft_notes_api`, or if the opt-out leaked into the shared `post()`
    default and started applying to every endpoint.
    """
    captured: Request | None = None

    async def handler(request: Request) -> Response:
        nonlocal captured
        captured = request
        return Response(status_code=200, request=request, json={})

    async with AsyncClient(
            base_url="https://gitlab.test",
            transport=MockTransport(handler),
    ) as http_client:
        gitlab_mr_client = GitLabMergeRequestsHTTPClient(client=http_client)

        await gitlab_mr_client.bulk_publish_draft_notes_api(project_id="1", merge_request_id="2")
        assert captured is not None
        assert captured.extensions.get(NO_RETRY_EXTENSION) is True

        await gitlab_mr_client.create_note_api(
            project_id="1",
            merge_request_id="2",
            request=GitLabCreateMRNoteRequestSchema(body="hello"),
        )
        assert not captured.extensions.get(NO_RETRY_EXTENSION)
