from ai_review.services.review.service import ReviewService


async def run_clear_inline_review():
    async with ReviewService() as review_service:
        await review_service.run_clear_inline_review()
