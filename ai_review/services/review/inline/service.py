import re

from pydantic import ValidationError

from ai_review.libs.json import sanitize_json_string
from ai_review.libs.logger import get_logger
from ai_review.services.review.inline.schema import InlineCommentListSchema
from ai_review.services.review.inline.types import InlineCommentServiceProtocol

logger = get_logger("INLINE_COMMENT_SERVICE")

FIRST_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*]", re.MULTILINE)
CLEAN_JSON_BLOCK_RE = re.compile(r"```(?:json)?(.*?)```", re.DOTALL | re.IGNORECASE)


class InlineCommentService(InlineCommentServiceProtocol):
    @classmethod
    def try_parse_model_output(cls, raw: str) -> InlineCommentListSchema | None:
        try:
            return InlineCommentListSchema.model_validate_json(raw)
        except ValidationError as error:
            logger.warning(f"Parse failed, trying sanitized JSON: {raw[:200]=}, {error=}")
            try:
                cleaned = sanitize_json_string(raw)
                return InlineCommentListSchema.model_validate_json(cleaned)
            except ValidationError as error:
                logger.warning(f"Sanitized JSON still invalid: {raw[:200]=}, {error=}")
                return None

    @classmethod
    def parse_model_output(cls, output: str) -> InlineCommentListSchema:
        output = (output or "").strip()
        if not output:
            logger.warning("️LLM returned empty string for inline review")
            return InlineCommentListSchema(root=[])

        if match := CLEAN_JSON_BLOCK_RE.search(output):
            output = match.group(1).strip()

        if parsed := cls.try_parse_model_output(output):
            return parsed

        logger.warning("Failed to parse LLM output as JSON, trying to extract first JSON array...")

        if json_array_match := FIRST_JSON_ARRAY_RE.search(output):
            if parsed := cls.try_parse_model_output(json_array_match.group(0)):
                logger.info("Successfully parsed JSON after extracting array from output")
                return parsed
            else:
                logger.error("Extracted JSON array is still invalid after sanitization")
        else:
            logger.error("No JSON array found in LLM output")

        return InlineCommentListSchema(root=[])
