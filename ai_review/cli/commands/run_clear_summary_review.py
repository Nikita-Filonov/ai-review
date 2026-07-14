from ai_review.services.review.service import ReviewService


async def run_clear_summary_review():
    review_service = ReviewService()
    await review_service.run_clear_summary_review()
