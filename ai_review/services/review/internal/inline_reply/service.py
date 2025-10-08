from ai_review.libs.llm.output_json_parser import LLMOutputJSONParser
from ai_review.libs.logger import get_logger
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.inline_reply.types import InlineCommentReplyServiceProtocol

logger = get_logger("INLINE_COMMENT_REPLY_SERVICE")


class InlineCommentReplyService(InlineCommentReplyServiceProtocol):
    def __init__(self):
        self.parser = LLMOutputJSONParser(model=InlineCommentReplySchema)

    def parse_model_output(self, output: str) -> InlineCommentReplySchema | None:
        logger.debug("Parsing LLM output for inline reply...")
        parsed = self.parser.parse_output(output)
        if parsed:
            logger.debug("Inline reply parsed successfully")
        else:
            logger.warning("Inline reply parse failed or model returned empty JSON")
        return parsed
