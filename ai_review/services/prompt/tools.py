import re

from ai_review.libs.logger import get_logger
from ai_review.services.diff.schema import DiffFileSchema

logger = get_logger("PROMPT_TOOLS")


def format_file(diff: DiffFileSchema) -> str:
    return f"# File: {diff.file}\n{diff.diff}\n"


def normalize_prompt(text: str) -> str:
    tails_stripped = [re.sub(r"[ \t]+$", "", line) for line in text.splitlines()]
    text = "\n".join(tails_stripped)

    text = re.sub(r"\n{3,}", "\n\n", text)

    result = text.strip()
    if len(text) > len(result):
        logger.info(f"Prompt has been normalized from {len(text)} to {len(result)}")
        return result

    return text
