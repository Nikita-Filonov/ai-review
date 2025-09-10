from __future__ import annotations

import re

from pydantic import ValidationError

from libs.logger import get_logger
from services.review.inline.schema import InlineCommentListSchema

logger = get_logger("INLINE_COMMENT_SERVICE")

FIRST_JSON_ARRAY_RE = re.compile(r"\[.*]", re.DOTALL)


class InlineCommentService:
    @classmethod
    def parse_model_output(cls, output: str) -> InlineCommentListSchema:
        output = (output or "").strip()
        if not output:
            logger.warning("️LLM returned empty string for inline review")
            return InlineCommentListSchema(root=[])

        try:
            return InlineCommentListSchema.model_validate_json(output)
        except ValidationError:
            logger.warning("LLM output is not valid JSON, trying to extract first JSON array...")

        json_array_match = FIRST_JSON_ARRAY_RE.search(output)
        if json_array_match:
            try:
                return InlineCommentListSchema.model_validate_json(json_array_match.group(0))
            except ValidationError:
                logger.error("JSON array found but still invalid")
        else:
            logger.error("No JSON array found in LLM output")

        return InlineCommentListSchema(root=[])
