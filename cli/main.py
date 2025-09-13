import asyncio

import typer

from cli.commands.run_inline_review import run_inline_review_command
from cli.commands.run_review import run_review_command
from cli.commands.run_summary_review import run_summary_review_command

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


@app.command("run-summary")
def run_summary():
    """Run only the summary review"""
    typer.secho("Starting summary AI review...", fg=typer.colors.CYAN)
    asyncio.run(run_summary_review_command())
    typer.secho("AI review completed successfully!", fg=typer.colors.GREEN, bold=True)


if __name__ == "__main__":
    app()
