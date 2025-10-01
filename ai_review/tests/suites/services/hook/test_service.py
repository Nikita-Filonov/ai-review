import pytest

from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.hook.constants import HookType
from ai_review.services.hook.service import HookService


@pytest.fixture
def hook_service() -> HookService:
    """Return a fresh HookService instance for each test."""
    return HookService()


@pytest.mark.asyncio
async def test_inject_and_emit_simple(hook_service: HookService):
    """
    Should register hook and invoke it with emitted args.
    """
    results = []

    async def sample_hook(arg1: str, arg2: int):
        results.append((arg1, arg2))

    hook_service.inject_hook(HookType.ON_CHAT_START, sample_hook)
    await hook_service.emit(HookType.ON_CHAT_START, "hi", 42)

    assert results == [("hi", 42)]


@pytest.mark.asyncio
async def test_emit_without_hooks_does_nothing(hook_service: HookService):
    """
    If no hooks are registered, emit should silently return.
    """
    await hook_service.emit(HookType.ON_CHAT_COMPLETE, "text")


@pytest.mark.asyncio
async def test_emit_handles_hook_exception(monkeypatch: pytest.MonkeyPatch, hook_service: HookService):
    """
    Should catch exceptions in hook and log them, without breaking flow.
    """
    errors = []

    async def failing_hook():
        raise ValueError("Boom!")

    def fake_logger_exception(message: str):
        errors.append(message)

    monkeypatch.setattr("ai_review.services.hook.service.logger.exception", fake_logger_exception)
    hook_service.inject_hook(HookType.ON_CHAT_COMPLETE, failing_hook)

    await hook_service.emit(HookType.ON_CHAT_COMPLETE)
    assert any("Boom!" in message for message in errors)


@pytest.mark.asyncio
async def test_on_chat_start_decorator_registers_hook(hook_service: HookService):
    """
    Using @on_chat_start should register the callback.
    """
    results = []

    @hook_service.on_chat_start
    async def chat_start_hook(prompt: str, prompt_system: str):
        results.append((prompt, prompt_system))

    await hook_service.emit_chat_start("Hello", "SYS")
    assert results == [("Hello", "SYS")]


@pytest.mark.asyncio
async def test_on_chat_complete_decorator_registers_hook(hook_service: HookService):
    """
    Using @on_chat_complete should register and trigger hook.
    """
    results = []

    @hook_service.on_chat_complete
    async def chat_complete_hook(result: str, report: CostReportSchema | None):
        results.append((result, report))

    cost_report = CostReportSchema(
        model="gpt",
        prompt_tokens=10,
        completion_tokens=100,
        total_cost=26,
        input_cost=10.5,
        output_cost=15.5
    )
    await hook_service.emit_chat_complete("done", cost_report)
    assert results == [("done", cost_report)]
