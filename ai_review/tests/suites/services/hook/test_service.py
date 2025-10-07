import pytest

from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.hook.constants import HookType
from ai_review.services.hook.service import HookService
from ai_review.services.review.internal.inline.schema import InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema

cost_report = CostReportSchema(
    model="gpt",
    prompt_tokens=1,
    completion_tokens=2,
    total_cost=0.3,
    input_cost=0.1,
    output_cost=0.2
)
inline_comment = InlineCommentSchema(file="a.py", line=1, message="fix this")
inline_reply = InlineCommentReplySchema(message="ok", suggestion="use helper()")
summary_comment = SummaryCommentSchema(text="summary text")
summary_reply = SummaryCommentReplySchema(text="reply summary")

HOOK_CASES = [
    # Chat
    ("on_chat_start", "emit_chat_start", dict(prompt="hi", prompt_system="sys")),
    ("on_chat_error", "emit_chat_error", dict(prompt="oops", prompt_system="sys")),
    ("on_chat_complete", "emit_chat_complete", dict(result="done", report=cost_report)),

    # Inline Review
    ("on_inline_review_start", "emit_inline_review_start", {}),
    ("on_inline_review_complete", "emit_inline_review_complete", dict(report=cost_report)),

    # Context Review
    ("on_context_review_start", "emit_context_review_start", {}),
    ("on_context_review_complete", "emit_context_review_complete", dict(report=cost_report)),

    # Summary Review
    ("on_summary_review_start", "emit_summary_review_start", {}),
    ("on_summary_review_complete", "emit_summary_review_complete", dict(report=cost_report)),

    # Inline Reply Review
    ("on_inline_reply_review_start", "emit_inline_reply_review_start", {}),
    ("on_inline_reply_review_complete", "emit_inline_reply_review_complete", dict(report=cost_report)),

    # Summary Reply Review
    ("on_summary_reply_review_start", "emit_summary_reply_review_start", {}),
    ("on_summary_reply_review_complete", "emit_summary_reply_review_complete", dict(report=cost_report)),

    # Inline Comment
    ("on_inline_comment_start", "emit_inline_comment_start", dict(comment=inline_comment)),
    ("on_inline_comment_error", "emit_inline_comment_error", dict(comment=inline_comment)),
    ("on_inline_comment_complete", "emit_inline_comment_complete", dict(comment=inline_comment)),

    # Summary Comment
    ("on_summary_comment_start", "emit_summary_comment_start", dict(comment=summary_comment)),
    ("on_summary_comment_error", "emit_summary_comment_error", dict(comment=summary_comment)),
    ("on_summary_comment_complete", "emit_summary_comment_complete", dict(comment=summary_comment)),

    # Inline Comment Reply
    ("on_inline_comment_reply_start", "emit_inline_comment_reply_start", dict(comment=inline_reply)),
    ("on_inline_comment_reply_error", "emit_inline_comment_reply_error", dict(comment=inline_reply)),
    ("on_inline_comment_reply_complete", "emit_inline_comment_reply_complete", dict(comment=inline_reply)),

    # Summary Comment Reply
    ("on_summary_comment_reply_start", "emit_summary_comment_reply_start", dict(comment=summary_reply)),
    ("on_summary_comment_reply_error", "emit_summary_comment_reply_error", dict(comment=summary_reply)),
    ("on_summary_comment_reply_complete", "emit_summary_comment_reply_complete", dict(comment=summary_reply)),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("inject_method, emit_method, args", HOOK_CASES)
async def test_all_hooks_trigger_correctly(
        hook_service: HookService,
        inject_method: str,
        emit_method: str,
        args: dict,
):
    """
    Ensure every hook registration + emit combination works correctly.
    Each hook should receive the emitted arguments without raising.
    """
    called = {}

    async def sample_hook(**kwargs):
        called.update(kwargs)

    emit_func = getattr(hook_service, emit_method)
    inject_func = getattr(hook_service, inject_method)

    inject_func(sample_hook)
    await emit_func(**args)

    assert called == args


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
