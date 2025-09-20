from ai_review.services.review.service import ReviewService


async def run_inline_review_command():
    review_service = ReviewService()
    await review_service.run_inline_review()
    review_service.report_total_cost()
