from unittest.mock import Mock, call

import httpx
import pytest

from ai_review.libs.http.event_hooks.logger import LoggerEventHook


@pytest.mark.asyncio
async def test_http_logger_hooks_include_method_url_and_status() -> None:
    logger = Mock()
    hook = LoggerEventHook(logger)
    request = httpx.Request("POST", "https://example.test/chat")
    response = httpx.Response(202, request=request)

    await hook.request(request)
    await hook.response(response)

    assert logger.info.call_args_list == [
        call("POST https://example.test/chat - Waiting for response"),
        call("POST https://example.test/chat - Status 202"),
    ]
