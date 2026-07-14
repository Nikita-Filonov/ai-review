from ai_review.services.review.service import ReviewService


async def run_inline_reply_review_command():
    async with ReviewService() as review_service:
        await review_service.run_inline_reply_review()
        review_service.report_total_cost()
