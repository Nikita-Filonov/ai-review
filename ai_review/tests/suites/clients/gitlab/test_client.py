import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.gitlab.client import get_gitlab_http_client, GitLabHTTPClient
from ai_review.clients.gitlab.mr.client import GitLabMergeRequestsHTTPClient
from ai_review.clients.gitlab.mr.schema.discussions import GitLabCreateMRDiscussionRequestSchema
from ai_review.clients.gitlab.mr.schema.draft_notes import GitLabCreateMRDraftNoteRequestSchema
from ai_review.clients.gitlab.mr.schema.notes import GitLabCreateMRNoteRequestSchema
from ai_review.clients.gitlab.mr.schema.position import GitLabPositionSchema
from ai_review.libs.http.transports.retry import NO_RETRY_EXTENSION


async def post_discussion_position(position: GitLabPositionSchema) -> dict[str, object]:
    requests: list[Request] = []

    async def handler(request: Request) -> Response:
        requests.append(request)
        return Response(status_code=200, request=request, json={})

    async with AsyncClient(base_url="https://gitlab.test", transport=MockTransport(handler)) as http_client:
        gitlab_mr_client = GitLabMergeRequestsHTTPClient(client=http_client)
        await gitlab_mr_client.create_discussion_api(
            project_id="1",
            merge_request_id="2",
            request=GitLabCreateMRDiscussionRequestSchema(body="finding", position=position),
        )

    assert len(requests) == 1
    return json.loads(requests[0].content)["position"]


async def post_draft_position(position: GitLabPositionSchema) -> dict[str, object]:
    requests: list[Request] = []

    async def handler(request: Request) -> Response:
        requests.append(request)
        return Response(status_code=200, request=request, json={})

    async with AsyncClient(base_url="https://gitlab.test", transport=MockTransport(handler)) as http_client:
        gitlab_mr_client = GitLabMergeRequestsHTTPClient(client=http_client)
        await gitlab_mr_client.create_draft_note_api(
            project_id="1",
            merge_request_id="2",
            request=GitLabCreateMRDraftNoteRequestSchema(note="finding", position=position),
        )

    assert len(requests) == 1
    return json.loads(requests[0].content)["position"]


def make_position(*, old_line: int | None, new_line: int | None) -> GitLabPositionSchema:
    return GitLabPositionSchema(
        position_type="text",
        base_sha="base-sha",
        head_sha="head-sha",
        start_sha="start-sha",
        old_path="src/file.py",
        new_path="src/file.py",
        old_line=old_line,
        new_line=new_line,
    )


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


@pytest.mark.asyncio
async def test_discussion_api_serializes_complete_context_position() -> None:
    """A discussion must receive both sides of an unchanged diff line."""
    serialized_position = await post_discussion_position(make_position(old_line=129, new_line=131))

    assert serialized_position == {
        "position_type": "text",
        "base_sha": "base-sha",
        "head_sha": "head-sha",
        "start_sha": "start-sha",
        "old_path": "src/file.py",
        "new_path": "src/file.py",
        "old_line": 129,
        "new_line": 131,
        "line_range": None,
    }


@pytest.mark.asyncio
async def test_draft_api_serializes_complete_context_position() -> None:
    """A draft note must receive both sides of an unchanged diff line."""
    serialized_position = await post_draft_position(make_position(old_line=129, new_line=131))

    assert serialized_position == {
        "position_type": "text",
        "base_sha": "base-sha",
        "head_sha": "head-sha",
        "start_sha": "start-sha",
        "old_path": "src/file.py",
        "new_path": "src/file.py",
        "old_line": 129,
        "new_line": 131,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("old_line", "new_line"),
    [(None, 42), (41, None)],
    ids=["added-line", "removed-line"],
)
async def test_discussion_api_serializes_side_specific_positions(
        old_line: int | None,
        new_line: int | None,
) -> None:
    """Discussions keep the coordinate of the side where the diff line exists."""
    serialized_position = await post_discussion_position(
        make_position(old_line=old_line, new_line=new_line)
    )

    assert serialized_position["old_path"] == "src/file.py"
    assert serialized_position["new_path"] == "src/file.py"
    assert serialized_position["old_line"] == old_line
    assert serialized_position["new_line"] == new_line


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("old_line", "new_line", "expected_lines"),
    [
        (None, 42, {"new_line": 42}),
        (41, None, {"old_line": 41}),
    ],
    ids=["added-line", "removed-line"],
)
async def test_draft_api_serializes_side_specific_positions(
        old_line: int | None,
        new_line: int | None,
        expected_lines: dict[str, int],
) -> None:
    """Draft notes omit the coordinate for the side where the diff line does not exist."""
    serialized_position = await post_draft_position(
        make_position(old_line=old_line, new_line=new_line)
    )

    assert serialized_position["old_path"] == "src/file.py"
    assert serialized_position["new_path"] == "src/file.py"
    assert {
        key: value
        for key, value in serialized_position.items()
        if key in {"old_line", "new_line"}
    } == expected_lines
