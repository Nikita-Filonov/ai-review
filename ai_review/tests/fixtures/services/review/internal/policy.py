from typing import Any

import pytest

from ai_review.services.review.internal.policy.types import ReviewPolicyServiceProtocol


class FakeReviewPolicyService(ReviewPolicyServiceProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    def apply_for_files(self, files: list[str]) -> list[str]:
        self.calls.append(("apply_for_files", {"files": files}))
        return self.responses.get("apply_for_files", files)

    def apply_for_inline_comments(self, comments: list) -> list:
        self.calls.append(("apply_for_inline_comments", {"comments": comments}))
        return self.responses.get("apply_for_inline_comments", comments)

    def apply_for_context_comments(self, comments: list) -> list:
        self.calls.append(("apply_for_context_comments", {"comments": comments}))
        return self.responses.get("apply_for_context_comments", comments)


@pytest.fixture
def fake_review_policy_service() -> FakeReviewPolicyService:
    return FakeReviewPolicyService()
