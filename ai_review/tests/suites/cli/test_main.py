import pytest
from typer.testing import CliRunner

from ai_review.cli.main import app
from ai_review.services.review.service import ReviewService

runner = CliRunner()


@pytest.fixture(autouse=True)
def dummy_review_service(monkeypatch: pytest.MonkeyPatch, review_service: ReviewService):
    monkeypatch.setattr("ai_review.cli.commands.run_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_inline_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_context_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_summary_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_inline_reply_review.ReviewService", lambda: review_service)
    monkeypatch.setattr("ai_review.cli.commands.run_summary_reply_review.ReviewService", lambda: review_service)


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
def test_cli_commands_invoke_review_service_successfully(args: list[str], expected_output: str):
    """
    Ensure CLI commands correctly call the ReviewService with fake dependencies.
    """
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert expected_output in result.output
    assert "AI review completed successfully!" in result.output


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
