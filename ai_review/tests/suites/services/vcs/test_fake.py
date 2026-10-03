import pytest

from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_fake_create_general_comment_raises_configured_error() -> None:
    failure = RuntimeError("provider failed")
    fake = FakeVCSClient(responses={"create_general_comment_error": failure})

    with pytest.raises(RuntimeError) as caught:
        await fake.create_general_comment("message")

    assert caught.value is failure
    assert fake.calls == [("create_general_comment", ("message",), {})]


@pytest.mark.asyncio
async def test_fake_create_inline_comment_raises_configured_error() -> None:
    failure = RuntimeError("provider failed")
    fake = FakeVCSClient(responses={"create_inline_comment_error": failure})

    with pytest.raises(RuntimeError) as caught:
        await fake.create_inline_comment("file.py", 1, "message")

    assert caught.value is failure
    assert fake.calls == [("create_inline_comment", ("file.py", 1, "message"), {})]


@pytest.mark.asyncio
async def test_fake_delete_general_comment_raises_configured_error() -> None:
    failure = RuntimeError("provider failed")
    fake = FakeVCSClient(responses={"delete_general_comment_error": failure})

    with pytest.raises(RuntimeError) as caught:
        await fake.delete_general_comment("1")

    assert caught.value is failure
    assert fake.calls == [("delete_general_comment", ("1",), {})]


@pytest.mark.asyncio
async def test_fake_delete_inline_comment_raises_configured_error() -> None:
    failure = RuntimeError("provider failed")
    fake = FakeVCSClient(responses={"delete_inline_comment_error": failure})

    with pytest.raises(RuntimeError) as caught:
        await fake.delete_inline_comment("1")

    assert caught.value is failure
    assert fake.calls == [("delete_inline_comment", ("1",), {})]


@pytest.mark.asyncio
async def test_fake_create_inline_reply_raises_configured_error() -> None:
    failure = RuntimeError("provider failed")
    fake = FakeVCSClient(responses={"create_inline_reply_error": failure})

    with pytest.raises(RuntimeError) as caught:
        await fake.create_inline_reply("1", "message")

    assert caught.value is failure
    assert fake.calls == [("create_inline_reply", ("1", "message"), {})]
