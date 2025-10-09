from typing import Any

import pytest

from ai_review.services.review.gateway.review_dry_run_comment_gateway import ReviewDryRunCommentGateway
from ai_review.services.review.gateway.types import ReviewCommentGatewayProtocol
from ai_review.services.review.internal.inline.schema import InlineCommentSchema, InlineCommentListSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import (
    UserSchema,
    ThreadKind,
    ReviewThreadSchema,
    ReviewCommentSchema,
    VCSClientProtocol,
)


class FakeReviewDryRunCommentGateway(ReviewCommentGatewayProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []

        fake_user = UserSchema(id="u1", username="tester", name="Tester")

        fake_inline_thread = ReviewThreadSchema(
            id="t1",
            kind=ThreadKind.INLINE,
            file="file.py",
            line=10,
            comments=[
                ReviewCommentSchema(
                    id="c1",
                    body="#ai-review-inline some comment",
                    file="file.py",
                    line=10,
                    author=fake_user,
                ),
            ],
        )

        fake_summary_thread = ReviewThreadSchema(
            id="t2",
            kind=ThreadKind.SUMMARY,
            comments=[
                ReviewCommentSchema(
                    id="c2",
                    body="#ai-review-summary summary comment",
                    author=fake_user,
                ),
            ],
        )

        self.responses = responses or {
            "get_inline_threads": [fake_inline_thread],
            "get_summary_threads": [fake_summary_thread],
            "has_existing_inline_comments": False,
            "has_existing_summary_comments": False,
        }

    # --- Методы чтения ---
    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        self.calls.append(("get_inline_threads", {}))
        return self.responses["get_inline_threads"]

    async def get_summary_threads(self) -> list[ReviewThreadSchema]:
        self.calls.append(("get_summary_threads", {}))
        return self.responses["get_summary_threads"]

    async def has_existing_inline_comments(self) -> bool:
        self.calls.append(("has_existing_inline_comments", {}))
        return self.responses["has_existing_inline_comments"]

    async def has_existing_summary_comments(self) -> bool:
        self.calls.append(("has_existing_summary_comments", {}))
        return self.responses["has_existing_summary_comments"]

    async def process_inline_reply(self, thread_id: str, reply: InlineCommentReplySchema) -> None:
        self.calls.append(("process_inline_reply", {"thread_id": thread_id, "reply": reply}))

    async def process_summary_reply(self, thread_id: str, reply: SummaryCommentReplySchema) -> None:
        self.calls.append(("process_summary_reply", {"thread_id": thread_id, "reply": reply}))

    async def process_inline_comment(self, comment: InlineCommentSchema) -> None:
        self.calls.append(("process_inline_comment", {"comment": comment}))

    async def process_summary_comment(self, comment: SummaryCommentSchema) -> None:
        self.calls.append(("process_summary_comment", {"comment": comment}))

    async def process_inline_comments(self, comments: InlineCommentListSchema) -> None:
        self.calls.append(("process_inline_comments", {"comments": comments}))
        for comment in comments.root:
            await self.process_inline_comment(comment)


@pytest.fixture
def fake_review_dry_run_comment_gateway() -> FakeReviewDryRunCommentGateway:
    return FakeReviewDryRunCommentGateway()


@pytest.fixture
def review_dry_run_comment_gateway(fake_vcs_client: VCSClientProtocol) -> ReviewDryRunCommentGateway:
    return ReviewDryRunCommentGateway(vcs=fake_vcs_client)
