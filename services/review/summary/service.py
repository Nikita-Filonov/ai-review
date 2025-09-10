from libs.logger import get_logger
from services.review.summary.schema import SummaryCommentSchema

logger = get_logger("SUMMARY_COMMENT_SERVICE")


class SummaryCommentService:
    @classmethod
    def parse_model_output(cls, output: str) -> SummaryCommentSchema:
        text = (output or "").strip()
        if not text:
            logger.warning("LLM returned empty summary")

        return SummaryCommentSchema(text=text)
