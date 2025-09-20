import re

from pydantic import ValidationError

from ai_review.libs.logger import get_logger
from ai_review.services.review.inline.schema import InlineCommentListSchema

logger = get_logger("INLINE_COMMENT_SERVICE")

FIRST_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*]", re.MULTILINE)
CLEAN_JSON_BLOCK_RE = re.compile(r"```(?:json)?(.*?)```", re.DOTALL | re.IGNORECASE)


class InlineCommentService:
    @classmethod
    def parse_model_output(cls, output: str) -> InlineCommentListSchema:
        output = (output or "").strip()
        if not output:
            logger.warning("️LLM returned empty string for inline review")
            return InlineCommentListSchema(root=[])

        if match := CLEAN_JSON_BLOCK_RE.search(output):
            output = match.group(1).strip()

        try:
            return InlineCommentListSchema.model_validate_json(output)
        except ValidationError:
            logger.warning("LLM output is not valid JSON, trying to extract first JSON array...")

        if json_array_match := FIRST_JSON_ARRAY_RE.search(output):
            try:
                return InlineCommentListSchema.model_validate_json(json_array_match.group(0))
            except ValidationError:
                logger.exception("JSON array found but still invalid")
        else:
            logger.exception("No JSON array found in LLM output")

        return InlineCommentListSchema(root=[])
