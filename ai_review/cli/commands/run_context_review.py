from ai_review.services.review.service import ReviewService


async def run_context_review_command():
    async with ReviewService() as review_service:
        await review_service.run_context_review()
        review_service.report_total_cost()
