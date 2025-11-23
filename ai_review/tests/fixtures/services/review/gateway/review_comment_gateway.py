from typing import Any

import pytest

from ai_review.services.artifacts.types import ArtifactsServiceProtocol
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
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
    VCSClientProtocol
)


class FakeReviewCommentGateway(ReviewCommentGatewayProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []

        fake_user = UserSchema(id="u1", username="tester", name="Tester")

        fake_inline_thread = ReviewThreadSchema(
            id="t1",
            kind=ThreadKind.INLINE,
            file="file.py",
            line=5,
            comments=[
                ReviewCommentSchema(
                    id="c1",
                    body="AI inline comment <!--AI-->",
                    file="file.py",
                    line=5,
                    author=fake_user
                ),
                ReviewCommentSchema(id="c2", body="Developer reply", file="file.py", line=5, author=fake_user),
            ],
        )

        fake_summary_thread = ReviewThreadSchema(
            id="t2",
            kind=ThreadKind.SUMMARY,
            comments=[
                ReviewCommentSchema(id="c3", body="AI summary comment <!--AI-->", author=fake_user),
                ReviewCommentSchema(id="c4", body="Developer reply", author=fake_user),
            ],
        )

        self.responses = responses or {
            "get_inline_threads": [fake_inline_thread],
            "get_summary_threads": [fake_summary_thread],
            "has_existing_inline_comments": False,
            "has_existing_summary_comments": False,
        }

    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        self.calls.append(("get_inline_threads", {}))
        return self.responses.get("get_inline_threads", [])

    async def get_summary_threads(self) -> list[ReviewThreadSchema]:
        self.calls.append(("get_summary_threads", {}))
        return self.responses.get("get_summary_threads", [])

    async def has_existing_inline_comments(self) -> bool:
        self.calls.append(("has_existing_inline_comments", {}))
        return self.responses.get("has_existing_inline_comments", False)

    async def has_existing_summary_comments(self) -> bool:
        self.calls.append(("has_existing_summary_comments", {}))
        return self.responses.get("has_existing_summary_comments", False)

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


@pytest.fixture
def fake_review_comment_gateway() -> FakeReviewCommentGateway:
    return FakeReviewCommentGateway()


@pytest.fixture
def review_comment_gateway(
        fake_vcs_client: VCSClientProtocol,
        fake_artifacts_service: ArtifactsServiceProtocol
) -> ReviewCommentGateway:
    return ReviewCommentGateway(vcs=fake_vcs_client, artifacts=fake_artifacts_service)
