import asyncio

import typer

from ai_review.cli.commands.run_context_review import run_context_review_command
from ai_review.cli.commands.run_inline_reply_review import run_inline_reply_review_command
from ai_review.cli.commands.run_inline_review import run_inline_review_command
from ai_review.cli.commands.run_review import run_review_command
from ai_review.cli.commands.run_summary_reply_review import run_summary_reply_review_command
from ai_review.cli.commands.run_summary_review import run_summary_review_command
from ai_review.config import settings

app = typer.Typer(help="AI Review CLI")


@app.command("run")
def run():
    """Run the full AI review pipeline"""
    typer.secho("Starting full AI review...", fg=typer.colors.CYAN, bold=True)
    asyncio.run(run_review_command())
    typer.secho("AI review completed successfully!", fg=typer.colors.GREEN, bold=True)


@app.command("run-inline")
def run_inline():
    """Run only the inline review"""
    typer.secho("Starting inline AI review...", fg=typer.colors.CYAN)
    asyncio.run(run_inline_review_command())
    typer.secho("AI review completed successfully!", fg=typer.colors.GREEN, bold=True)


@app.command("run-context")
def run_context():
    """Run only the context review"""
    typer.secho("Starting context AI review...", fg=typer.colors.CYAN)
    asyncio.run(run_context_review_command())
    typer.secho("AI review completed successfully!", fg=typer.colors.GREEN, bold=True)


@app.command("run-summary")
def run_summary():
    """Run only the summary review"""
    typer.secho("Starting summary AI review...", fg=typer.colors.CYAN)
    asyncio.run(run_summary_review_command())
    typer.secho("AI review completed successfully!", fg=typer.colors.GREEN, bold=True)


@app.command("run-inline-reply")
def run_inline_reply():
    """Run only the inline reply review"""
    typer.secho("Starting inline reply AI review...", fg=typer.colors.CYAN)
    asyncio.run(run_inline_reply_review_command())
    typer.secho("AI review completed successfully!", fg=typer.colors.GREEN, bold=True)


@app.command("run-summary-reply")
def run_summary_reply():
    typer.secho("Starting summary reply AI review...", fg=typer.colors.CYAN)
    asyncio.run(run_summary_reply_review_command())
    typer.secho("AI review completed successfully!", fg=typer.colors.GREEN, bold=True)


@app.command("show-config")
def show_config():
    """Show the current resolved configuration"""
    typer.secho("Loaded AI Review configuration:", fg=typer.colors.CYAN, bold=True)
    typer.echo(settings.model_dump_json(indent=2, exclude_none=True))


if __name__ == "__main__":
    app()
