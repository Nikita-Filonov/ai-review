from typing import Callable, Awaitable

from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.review.internal.inline.schema import InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema

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

InlineReplyReviewStartHookFunc = Callable[..., Awaitable[None]]
InlineReplyReviewCompleteHookFunc = Callable[[CostReportSchema | None], Awaitable[None]]

SummaryReplyReviewStartHookFunc = Callable[..., Awaitable[None]]
SummaryReplyReviewCompleteHookFunc = Callable[[CostReportSchema | None], Awaitable[None]]

InlineCommentStartHookFunc = Callable[[InlineCommentSchema], Awaitable[None]]
InlineCommentErrorHookFunc = Callable[[InlineCommentSchema], Awaitable[None]]
InlineCommentCompleteHookFunc = Callable[[InlineCommentSchema], Awaitable[None]]

SummaryCommentStartHookFunc = Callable[[SummaryCommentSchema], Awaitable[None]]
SummaryCommentErrorHookFunc = Callable[[SummaryCommentSchema], Awaitable[None]]
SummaryCommentCompleteHookFunc = Callable[[SummaryCommentSchema], Awaitable[None]]

InlineCommentReplyStartHookFunc = Callable[[InlineCommentReplySchema], Awaitable[None]]
InlineCommentReplyErrorHookFunc = Callable[[InlineCommentReplySchema], Awaitable[None]]
InlineCommentReplyCompleteHookFunc = Callable[[InlineCommentReplySchema], Awaitable[None]]

SummaryCommentReplyStartHookFunc = Callable[[SummaryCommentReplySchema], Awaitable[None]]
SummaryCommentReplyErrorHookFunc = Callable[[SummaryCommentReplySchema], Awaitable[None]]
SummaryCommentReplyCompleteHookFunc = Callable[[SummaryCommentReplySchema], Awaitable[None]]
