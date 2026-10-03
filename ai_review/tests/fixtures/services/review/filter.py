import pytest

from ai_review.services.review.filter.service import ReviewFilterService


@pytest.fixture
def review_filter_service() -> ReviewFilterService:
    return ReviewFilterService()
