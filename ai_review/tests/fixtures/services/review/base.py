import pytest

from ai_review.services.cost.types import CostServiceProtocol
from ai_review.services.review.runner.types import ReviewRunnerProtocol
from ai_review.services.review.service import ReviewService


@pytest.fixture
def review_service(
        monkeypatch: pytest.MonkeyPatch,
        fake_cost_service: CostServiceProtocol,
        fake_inline_review_runner: ReviewRunnerProtocol,
        fake_context_review_runner: ReviewRunnerProtocol,
        fake_summary_review_runner: ReviewRunnerProtocol,
        fake_inline_reply_review_runner: ReviewRunnerProtocol,
        fake_summary_reply_review_runner: ReviewRunnerProtocol,
):
    monkeypatch.setattr("ai_review.services.review.service.CostService", lambda: fake_cost_service)

    monkeypatch.setattr(
        "ai_review.services.review.service.InlineReviewRunner",
        lambda **_: fake_inline_review_runner
    )
    monkeypatch.setattr(
        "ai_review.services.review.service.ContextReviewRunner",
        lambda **_: fake_context_review_runner
    )
    monkeypatch.setattr(
        "ai_review.services.review.service.SummaryReviewRunner",
        lambda **_: fake_summary_review_runner
    )
    monkeypatch.setattr(
        "ai_review.services.review.service.InlineReplyReviewRunner",
        lambda **_: fake_inline_reply_review_runner
    )
    monkeypatch.setattr(
        "ai_review.services.review.service.SummaryReplyReviewRunner",
        lambda **_: fake_summary_reply_review_runner
    )

    return ReviewService()
