from unittest.mock import AsyncMock

import pytest

from ai_review.services.vcs.bitbucket_server.client import BitbucketServerVCSClient
from ai_review.services.vcs.types import ReviewInfoSchema


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_review_info_returns_empty_info_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failed_request = AsyncMock(side_effect=RuntimeError("BitbucketServer unavailable"))
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "get_pull_request", failed_request)

    result = await bitbucket_server_vcs_client.get_review_info()

    assert result == ReviewInfoSchema()
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_general_comments_returns_empty_list_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failed_request = AsyncMock(side_effect=RuntimeError("BitbucketServer unavailable"))
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "get_activities", failed_request)

    result = await bitbucket_server_vcs_client.get_general_comments()

    assert result == []
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_inline_comments_returns_empty_list_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failed_request = AsyncMock(side_effect=RuntimeError("BitbucketServer unavailable"))
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "get_activities", failed_request)

    result = await bitbucket_server_vcs_client.get_inline_comments()

    assert result == []
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_inline_threads_returns_empty_list_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failed_request = AsyncMock(side_effect=RuntimeError("BitbucketServer unavailable"))
    monkeypatch.setattr(bitbucket_server_vcs_client, "get_inline_comments", failed_request)

    result = await bitbucket_server_vcs_client.get_inline_threads()

    assert result == []
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_get_general_threads_returns_empty_list_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failed_request = AsyncMock(side_effect=RuntimeError("BitbucketServer unavailable"))
    monkeypatch.setattr(bitbucket_server_vcs_client, "get_general_comments", failed_request)

    result = await bitbucket_server_vcs_client.get_general_threads()

    assert result == []
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_general_comment_propagates_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failure = RuntimeError("BitbucketServer unavailable")
    failed_request = AsyncMock(side_effect=failure)
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "create_comment", failed_request)

    with pytest.raises(RuntimeError) as caught:
        await bitbucket_server_vcs_client.create_general_comment("message")

    assert caught.value is failure
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_inline_comment_propagates_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failure = RuntimeError("BitbucketServer unavailable")
    failed_request = AsyncMock(side_effect=failure)
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "create_comment", failed_request)

    with pytest.raises(RuntimeError) as caught:
        await bitbucket_server_vcs_client.create_inline_comment("file.py", 3, "message")

    assert caught.value is failure
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_delete_general_comment_propagates_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failure = RuntimeError("BitbucketServer unavailable")
    failed_request = AsyncMock(side_effect=failure)
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "delete_comment", failed_request)

    with pytest.raises(RuntimeError) as caught:
        await bitbucket_server_vcs_client.delete_general_comment(3)

    assert caught.value is failure
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_delete_inline_comment_propagates_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failure = RuntimeError("BitbucketServer unavailable")
    failed_request = AsyncMock(side_effect=failure)
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "delete_comment", failed_request)

    with pytest.raises(RuntimeError) as caught:
        await bitbucket_server_vcs_client.delete_inline_comment(3)

    assert caught.value is failure
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_inline_reply_propagates_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failure = RuntimeError("BitbucketServer unavailable")
    failed_request = AsyncMock(side_effect=failure)
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "create_comment", failed_request)

    with pytest.raises(RuntimeError) as caught:
        await bitbucket_server_vcs_client.create_inline_reply(3, "message")

    assert caught.value is failure
    failed_request.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures("bitbucket_server_http_client_config")
async def test_create_summary_reply_propagates_failure(
    monkeypatch: pytest.MonkeyPatch,
    bitbucket_server_vcs_client: BitbucketServerVCSClient,
) -> None:
    failure = RuntimeError("BitbucketServer unavailable")
    failed_request = AsyncMock(side_effect=failure)
    monkeypatch.setattr(bitbucket_server_vcs_client.http_client.pr, "create_comment", failed_request)

    with pytest.raises(RuntimeError) as caught:
        await bitbucket_server_vcs_client.create_summary_reply(3, "message")

    assert caught.value is failure
    failed_request.assert_awaited_once()
