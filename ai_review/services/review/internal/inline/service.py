import re

from ai_review.libs.llm.output_json_parser import LLMOutputJSONParser
from ai_review.libs.logger import get_logger
from ai_review.services.review.internal.inline.schema import InlineCommentListSchema
from ai_review.services.review.internal.inline.types import InlineCommentServiceProtocol

logger = get_logger("INLINE_COMMENT_SERVICE")

FIRST_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*]", re.MULTILINE)


class InlineCommentService(InlineCommentServiceProtocol):
    def __init__(self):
        self.parser = LLMOutputJSONParser(model=InlineCommentListSchema)

    def parse_model_output(self, output: str) -> InlineCommentListSchema:
        output = (output or "").strip()
        if not output:
            logger.warning("LLM returned empty string for inline review")
            return InlineCommentListSchema(root=[])

        if parsed := self.parser.parse_output(output):
            return parsed

        logger.warning("Failed to parse JSON, trying to extract first JSON array...")

        if json_array_match := FIRST_JSON_ARRAY_RE.search(output):
            extracted = json_array_match.group(0)
            logger.debug(f"Extracted potential JSON array (len={len(extracted)})")

            if parsed := self.parser.try_parse(extracted):
                logger.info("Successfully parsed JSON after extracting array from output")
                return parsed
            else:
                logger.error("Extracted JSON array is still invalid after sanitization")
        else:
            logger.error("No JSON array found in LLM output")

        return InlineCommentListSchema(root=[])
