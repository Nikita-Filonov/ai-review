import pytest

from ai_review.services.cost.schema import CalculateCostSchema
from ai_review.services.review.gateway.review_agent_llm_gateway import ReviewAgentLLMGateway
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.gateway.review_direct_llm_gateway import ReviewDirectLLMGateway
from ai_review.services.review.gateway.review_dry_run_comment_gateway import ReviewDryRunCommentGateway
from ai_review.services.review.service import ReviewService
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.review.runner.context import FakeContextReviewRunner
from ai_review.tests.fixtures.services.review.runner.inline import FakeInlineReviewRunner
from ai_review.tests.fixtures.services.review.runner.inline_reply import FakeInlineReplyReviewRunner
from ai_review.tests.fixtures.services.review.runner.summary import FakeSummaryReviewRunner
from ai_review.tests.fixtures.services.review.runner.summary_reply import FakeSummaryReplyReviewRunner


@pytest.mark.asyncio
async def test_run_inline_review_invokes_runner(
        review_service: ReviewService,
        fake_inline_review_runner: FakeInlineReviewRunner
):
    """Should call run() on InlineReviewRunner."""
    await review_service.run_inline_review()
    assert fake_inline_review_runner.calls == [("run", {})]


@pytest.mark.asyncio
async def test_run_context_review_invokes_runner(
        review_service: ReviewService,
        fake_context_review_runner: FakeContextReviewRunner
):
    """Should call run() on ContextReviewRunner."""
    await review_service.run_context_review()
    assert fake_context_review_runner.calls == [("run", {})]


@pytest.mark.asyncio
async def test_run_summary_review_invokes_runner(
        review_service: ReviewService,
        fake_summary_review_runner: FakeSummaryReviewRunner
):
    """Should call run() on SummaryReviewRunner."""
    await review_service.run_summary_review()
    assert fake_summary_review_runner.calls == [("run", {})]


@pytest.mark.asyncio
async def test_run_inline_reply_review_invokes_runner(
        review_service: ReviewService,
        fake_inline_reply_review_runner: FakeInlineReplyReviewRunner
):
    """Should call run() on InlineReplyReviewRunner."""
    await review_service.run_inline_reply_review()
    assert fake_inline_reply_review_runner.calls == [("run", {})]


@pytest.mark.asyncio
async def test_run_summary_reply_review_invokes_runner(
        review_service: ReviewService,
        fake_summary_reply_review_runner: FakeSummaryReplyReviewRunner
):
    """Should call run() on SummaryReplyReviewRunner."""
    await review_service.run_summary_reply_review()
    assert fake_summary_reply_review_runner.calls == [("run", {})]


def test_report_total_cost_with_data(
        capsys: pytest.CaptureFixture,
        review_service: ReviewService,
        fake_cost_service: FakeCostService
):
    """Should log total cost when cost report exists."""
    fake_cost_service.reports.append(
        fake_cost_service.calculate(
            result=CalculateCostSchema(
                prompt_tokens=50,
                completion_tokens=10,
            )
        )
    )

    review_service.report_total_cost()
    output = capsys.readouterr().out

    assert "TOTAL REVIEW COST" in output
    assert "fake-model" in output
    assert "0.006" in output


def test_report_total_cost_no_data(capsys: pytest.CaptureFixture, review_service: ReviewService):
    """Should log message when no cost data is available."""
    review_service.report_total_cost()
    output = capsys.readouterr().out

    assert "No cost data collected" in output


def test_review_service_uses_dry_run_comment_gateway(monkeypatch: pytest.MonkeyPatch):
    """Should use ReviewDryRunCommentGateway when settings.review.dry_run=True."""
    monkeypatch.setattr("ai_review.config.settings.review.dry_run", True)

    service = ReviewService()
    assert type(service.review_comment_gateway) is ReviewDryRunCommentGateway  # noqa


def test_review_service_uses_real_comment_gateway(monkeypatch: pytest.MonkeyPatch):
    """Should use normal ReviewCommentGateway when dry_run=False."""
    monkeypatch.setattr("ai_review.config.settings.review.dry_run", False)

    service = ReviewService()
    assert type(service.review_comment_gateway) is ReviewCommentGateway  # noqa


def test_review_service_initializes_agent_components():
    service = ReviewService()
    assert service.agent_loop is not None
    assert type(service.review_direct_llm_gateway) is ReviewDirectLLMGateway  # noqa


def test_review_service_uses_agent_gateway_when_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("ai_review.config.settings.agent.enabled", True)
    service = ReviewService()
    assert type(service.review_llm_gateway) is ReviewAgentLLMGateway


def test_review_service_uses_default_gateway_when_agent_disabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("ai_review.config.settings.agent.enabled", False)
    service = ReviewService()
    assert type(service.review_llm_gateway) is ReviewDirectLLMGateway
