import re
from typing import TypeVar, Generic, Type

from pydantic import BaseModel, ValidationError

from ai_review.libs.json import sanitize_json_string
from ai_review.libs.logger import get_logger

logger = get_logger("LLM_JSON_PARSER")

T = TypeVar("T", bound=BaseModel)

CLEAN_JSON_BLOCK_RE = re.compile(r"```(?:json)?(.*?)```", re.DOTALL | re.IGNORECASE)


def iter_json_candidates(raw: str):
    """Yield each top-level balanced {...} block found in *raw*.

    Handles strings with escaped quotes so that braces inside JSON string
    values are not counted.  When the prose before the real JSON payload
    contains stray curly braces (e.g. ``Some {note} here\\n{"key":"val"}``),
    every candidate is yielded and the caller decides which one is valid.
    """
    pos = 0
    length = len(raw)
    while pos < length:
        start = raw.find("{", pos)
        if start == -1:
            break
        depth = 0
        in_string = False
        escape = False
        for i in range(start, length):
            ch = raw[i]
            if escape:
                escape = False
                continue
            if ch == "\\" and in_string:
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    yield raw[start:i + 1]
                    pos = i + 1
                    break
        else:
            break


class LLMOutputJSONParser(Generic[T]):
    """Reusable JSON parser for LLM responses."""

    def __init__(self, model: Type[T]):
        self.model = model
        self.model_name = self.model.__name__

    def try_parse(self, raw: str) -> T | None:
        logger.debug(f"[{self.model_name}] Attempting JSON parse (len={len(raw)})")

        try:
            return self.model.model_validate_json(raw)
        except ValidationError as error:
            logger.warning(f"[{self.model_name}] Raw JSON parse failed: {error}")
            cleaned = sanitize_json_string(raw)

            if cleaned != raw:
                logger.debug(f"[{self.model_name}] Sanitized JSON differs, retrying parse...")
                try:
                    return self.model.model_validate_json(cleaned)
                except ValidationError as error:
                    logger.warning(f"[{self.model_name}] Sanitized JSON still invalid: {error}")
                    return None
            else:
                logger.debug(f"[{self.model_name}] Sanitized JSON identical — skipping retry")
                return None

    def parse_output(self, output: str) -> T | None:
        output = (output or "").strip()
        if not output:
            logger.warning(f"[{self.model_name}] Empty LLM output")
            return None

        logger.debug(f"[{self.model_name}] Parsing output (len={len(output)})")

        if match := CLEAN_JSON_BLOCK_RE.search(output):
            logger.debug(f"[{self.model_name}] Found fenced JSON block, extracting...")
            output = match.group(1).strip()

        if parsed := self.try_parse(output):
            logger.info(f"[{self.model_name}] Successfully parsed")
            return parsed

        for candidate in iter_json_candidates(output):
            if candidate == output:
                continue
            logger.debug(
                f"[{self.model_name}] Trying JSON candidate from noisy output "
                f"(candidate_len={len(candidate)}, original_len={len(output)})"
            )
            if parsed := self.try_parse(candidate):
                logger.info(f"[{self.model_name}] Successfully parsed JSON candidate from noisy output")
                return parsed

        logger.error(f"[{self.model_name}] No valid JSON found in output")
        return None
