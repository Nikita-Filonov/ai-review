import re

from ai_review.libs.logger import get_logger
from ai_review.services.agent.loop.schema import AgentTraceSchema
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.vcs.types import ReviewThreadSchema

logger = get_logger("PROMPT_TOOLS")


def format_file(diff: DiffFileSchema) -> str:
    return f"# File: {diff.file}\n{diff.diff}\n"


def format_files(diffs: list[DiffFileSchema]) -> str:
    return "\n\n".join(map(format_file, diffs))


def format_thread(thread: ReviewThreadSchema) -> str:
    if not thread.comments:
        return "No comments in thread."

    lines: list[str] = []
    for comment in thread.comments:
        user = (comment.author.name or comment.author.username or "User").strip()
        body = (comment.body or "").strip()
        if not body:
            continue

        lines.append(f"- {user}: {body}")

    return "\n\n".join(lines)


def normalize_prompt(text: str) -> str:
    tails_stripped = [re.sub(r"[ \t]+$", "", line) for line in text.splitlines()]
    text = "\n".join(tails_stripped)

    text = re.sub(r"\n{3,}", "\n\n", text)

    result = text.strip()
    if len(text) > len(result):
        logger.info(f"Prompt has been normalized from {len(text)} to {len(result)}")
        return result

    return text


def format_trace(trace: AgentTraceSchema) -> str:
    lines = [f"Iteration: {trace.iteration}"]

    if trace.step.command:
        lines.append(f"Command: {trace.step.command}")

    if trace.tool_output:
        lines.append(f"Tool output: {trace.tool_output}")

    if trace.step.content:
        lines.append(f"Content: {trace.step.content}")

    if trace.warning:
        lines.append(f"Warning: {trace.warning}")

    return "\n".join(lines)


def format_traces(traces: list[AgentTraceSchema]) -> str:
    if not traces:
        return "No previous steps."

    return "\n\n---\n\n".join(map(format_trace, traces))
