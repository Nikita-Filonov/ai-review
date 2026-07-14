import pytest
from typer.testing import CliRunner

from ai_review.cli.main import app
from ai_review.services.review.service import ReviewService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway

runner = CliRunner()


@pytest.fixture(autouse=True)
def dummy_review_service(
        monkeypatch: pytest.MonkeyPatch,
        review_service: ReviewService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    review_service.review_comment_gateway = fake_review_comment_gateway

    monkeypatch.setattr("ai_review.cli.commands.run_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_inline_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_context_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_summary_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_inline_reply_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_summary_reply_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_clear_inline_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_clear_summary_review.ReviewService", lambda: review_service)


@pytest.mark.parametrize(
    "args, expected_output",
    [
        (["run"], "Starting full AI review..."),
        (["run-inline"], "Starting inline AI review..."),
        (["run-context"], "Starting context AI review..."),
        (["run-summary"], "Starting summary AI review..."),
        (["run-inline-reply"], "Starting inline reply AI review..."),
        (["run-summary-reply"], "Starting summary reply AI review..."),
    ],
)
def test_cli_commands_invoke_review_service_successfully(
        args: list[str],
        expected_output: str,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """
    Ensure CLI commands correctly call the ReviewService with fake dependencies.
    """
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert expected_output in result.output
    assert "AI review completed successfully!" in result.output
    assert [call[0] for call in fake_review_comment_gateway.calls].count("finalize") == 1


@pytest.mark.parametrize(
    "args, expected_output, expected_call",
    [
        (["clear-inline"], "Clearing inline AI review comments...", "clear_inline_comments"),
        (["clear-summary"], "Clearing summary AI review comments...", "clear_summary_comments"),
    ],
)
def test_cli_clear_commands_do_not_finalize_review(
        args: list[str],
        expected_output: str,
        expected_call: str,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """
    Ensure cleanup commands run without entering the review finalization lifecycle.
    """
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert expected_output in result.output
    assert any(call[0] == expected_call for call in fake_review_comment_gateway.calls)
    assert all(call[0] != "finalize" for call in fake_review_comment_gateway.calls)


def test_show_config_outputs_json(monkeypatch: pytest.MonkeyPatch):
    """
    Validate that the 'show-config' command prints settings as JSON.
    """
    monkeypatch.setattr(
        "ai_review.cli.main.settings.model_dump_json",
        lambda **_: '{"debug": true}'
    )

    result = runner.invoke(app, ["show-config"])
    assert result.exit_code == 0
    assert "Loaded AI Review configuration" in result.output
    assert '{"debug": true}' in result.output
