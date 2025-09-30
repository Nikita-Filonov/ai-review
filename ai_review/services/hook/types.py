from typing import Callable, Awaitable

from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.review.inline.schema import InlineCommentSchema
from ai_review.services.review.summary.schema import SummaryCommentSchema

HookFunc = Callable[..., Awaitable[None]]

ChatStartHookFunc = Callable[[str, str], Awaitable[None]]
ChatErrorHookFunc = Callable[[str, str], Awaitable[None]]
ChatCompleteHookFunc = Callable[[str, CostReportSchema | None], Awaitable[None]]

InlineReviewStartHookFunc = Callable[..., Awaitable[None]]
InlineReviewCompleteHookFunc = Callable[[CostReportSchema | None], Awaitable[None]]

ContextReviewStartHookFunc = Callable[..., Awaitable[None]]
ContextReviewCompleteHookFunc = Callable[[CostReportSchema | None], Awaitable[None]]

SummaryReviewStartHookFunc = Callable[..., Awaitable[None]]
SummaryReviewCompleteHookFunc = Callable[[CostReportSchema | None], Awaitable[None]]

InlineCommentStartHookFunc = Callable[[InlineCommentSchema], Awaitable[None]]
InlineCommentErrorHookFunc = Callable[[InlineCommentSchema], Awaitable[None]]
InlineCommentCompleteHookFunc = Callable[[InlineCommentSchema], Awaitable[None]]

SummaryCommentStartHookFunc = Callable[[SummaryCommentSchema], Awaitable[None]]
SummaryCommentErrorHookFunc = Callable[[SummaryCommentSchema], Awaitable[None]]
SummaryCommentCompleteHookFunc = Callable[[SummaryCommentSchema], Awaitable[None]]
