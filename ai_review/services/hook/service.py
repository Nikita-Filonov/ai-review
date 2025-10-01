from collections import defaultdict
from typing import Any

from ai_review.libs.logger import get_logger
from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.hook.constants import HookType
from ai_review.services.hook.types import (
    HookFunc,
    # --- Chat ---
    ChatStartHookFunc,
    ChatErrorHookFunc,
    ChatCompleteHookFunc,
    # --- Inline Review ---
    InlineReviewStartHookFunc,
    InlineReviewCompleteHookFunc,
    # --- Context Review ---
    ContextReviewStartHookFunc,
    ContextReviewCompleteHookFunc,
    # --- Summary Review ---
    SummaryReviewStartHookFunc,
    SummaryReviewCompleteHookFunc,
    # --- Inline Comment ---
    InlineCommentStartHookFunc,
    InlineCommentErrorHookFunc,
    InlineCommentCompleteHookFunc,
    # --- Summary Comment ---
    SummaryCommentStartHookFunc,
    SummaryCommentCompleteHookFunc
)
from ai_review.services.review.inline.schema import InlineCommentSchema
from ai_review.services.review.summary.schema import SummaryCommentSchema

logger = get_logger("HOOK_SERVICE")


class HookService:
    def __init__(self):
        self.hooks: dict[HookType, list[HookFunc]] = defaultdict(list)

    def inject_hook(self, name: HookType, func: HookFunc):
        self.hooks[name].append(func)

    async def emit(self, name: HookType, *args: Any, **kwargs: Any):
        if not self.hooks.get(name):
            return

        for callback in self.hooks[name]:
            try:
                await callback(*args, **kwargs)
            except Exception as error:
                logger.exception(f"Error in {name} hook: {error}")

    # --- Chat ---
    def on_chat_start(self, func: ChatStartHookFunc):
        self.inject_hook(HookType.ON_CHAT_START, func)
        return func

    def on_chat_error(self, func: ChatErrorHookFunc):
        self.inject_hook(HookType.ON_CHAT_ERROR, func)
        return func

    def on_chat_complete(self, func: ChatCompleteHookFunc):
        self.inject_hook(HookType.ON_CHAT_COMPLETE, func)
        return func

    async def emit_chat_start(self, prompt: str, prompt_system: str):
        await self.emit(HookType.ON_CHAT_START, prompt=prompt, prompt_system=prompt_system)

    async def emit_chat_error(self, prompt: str, prompt_system: str):
        await self.emit(HookType.ON_CHAT_ERROR, prompt=prompt, prompt_system=prompt_system)

    async def emit_chat_complete(self, result: str, report: CostReportSchema | None):
        await self.emit(HookType.ON_CHAT_COMPLETE, result=result, report=report)

    # --- Inline Review ---
    def on_inline_review_start(self, func: InlineReviewStartHookFunc):
        self.inject_hook(HookType.ON_INLINE_REVIEW_START, func)
        return func

    def on_inline_review_complete(self, func: InlineReviewCompleteHookFunc):
        self.inject_hook(HookType.ON_INLINE_REVIEW_COMPLETE, func)
        return func

    async def emit_inline_review_start(self):
        await self.emit(HookType.ON_INLINE_REVIEW_START)

    async def emit_inline_review_complete(self, report: CostReportSchema | None):
        await self.emit(HookType.ON_INLINE_REVIEW_COMPLETE, report=report)

    # --- Context Review ---
    def on_context_review_start(self, func: ContextReviewStartHookFunc):
        self.inject_hook(HookType.ON_CONTEXT_REVIEW_START, func)
        return func

    def on_context_review_complete(self, func: ContextReviewCompleteHookFunc):
        self.inject_hook(HookType.ON_CONTEXT_REVIEW_COMPLETE, func)
        return func

    async def emit_context_review_start(self):
        await self.emit(HookType.ON_CONTEXT_REVIEW_START)

    async def emit_context_review_complete(self, report: CostReportSchema | None):
        await self.emit(HookType.ON_CONTEXT_REVIEW_COMPLETE, report=report)

    # --- Summary Review ---
    def on_summary_review_start(self, func: SummaryReviewStartHookFunc):
        self.inject_hook(HookType.ON_SUMMARY_REVIEW_START, func)
        return func

    def on_summary_review_complete(self, func: SummaryReviewCompleteHookFunc):
        self.inject_hook(HookType.ON_SUMMARY_REVIEW_COMPLETE, func)
        return func

    async def emit_summary_review_start(self):
        await self.emit(HookType.ON_SUMMARY_REVIEW_START)

    async def emit_summary_review_complete(self, report: CostReportSchema | None):
        await self.emit(HookType.ON_SUMMARY_REVIEW_COMPLETE, report=report)

    # --- Inline Comment ---
    def on_inline_comment_start(self, func: InlineCommentStartHookFunc):
        self.inject_hook(HookType.ON_INLINE_COMMENT_START, func)
        return func

    def on_inline_comment_error(self, func: InlineCommentErrorHookFunc):
        self.inject_hook(HookType.ON_INLINE_COMMENT_ERROR, func)
        return func

    def on_inline_comment_complete(self, func: InlineCommentCompleteHookFunc):
        self.inject_hook(HookType.ON_INLINE_COMMENT_COMPLETE, func)
        return func

    async def emit_inline_comment_start(self, comment: InlineCommentSchema):
        await self.emit(HookType.ON_INLINE_COMMENT_START, comment=comment)

    async def emit_inline_comment_error(self, comment: InlineCommentSchema):
        await self.emit(HookType.ON_INLINE_COMMENT_ERROR, comment=comment)

    async def emit_inline_comment_complete(self, comment: InlineCommentSchema):
        await self.emit(HookType.ON_INLINE_COMMENT_COMPLETE, comment=comment)

    # --- Summary Comment ---
    def on_summary_comment_start(self, func: SummaryCommentStartHookFunc):
        self.inject_hook(HookType.ON_SUMMARY_COMMENT_START, func)
        return func

    def on_summary_comment_error(self, func: InlineCommentErrorHookFunc):
        self.inject_hook(HookType.ON_SUMMARY_COMMENT_ERROR, func)
        return func

    def on_summary_comment_complete(self, func: SummaryCommentCompleteHookFunc):
        self.inject_hook(HookType.ON_SUMMARY_COMMENT_COMPLETE, func)
        return func

    async def emit_summary_comment_start(self, comment: SummaryCommentSchema):
        await self.emit(HookType.ON_SUMMARY_COMMENT_START, comment=comment)

    async def emit_summary_comment_error(self, comment: SummaryCommentSchema):
        await self.emit(HookType.ON_SUMMARY_COMMENT_ERROR, comment=comment)

    async def emit_summary_comment_complete(self, comment: SummaryCommentSchema):
        await self.emit(HookType.ON_SUMMARY_COMMENT_COMPLETE, comment=comment)
