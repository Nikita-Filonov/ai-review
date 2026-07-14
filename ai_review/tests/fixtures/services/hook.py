import pytest

from ai_review.services.hook import HookService
from ai_review.services.vcs.types import ReviewCommentSchema


class FakeHookService:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def emit_clear_inline_comments_start(self) -> None:
        self.calls.append(("emit_clear_inline_comments_start", {}))

    async def emit_clear_inline_comments_complete(self, comments: list[ReviewCommentSchema]) -> None:
        self.calls.append(("emit_clear_inline_comments_complete", {"comments": comments}))

    async def emit_clear_inline_comments_error(self) -> None:
        self.calls.append(("emit_clear_inline_comments_error", {}))

    async def emit_clear_summary_comments_start(self) -> None:
        self.calls.append(("emit_clear_summary_comments_start", {}))

    async def emit_clear_summary_comments_complete(self, comments: list[ReviewCommentSchema]) -> None:
        self.calls.append(("emit_clear_summary_comments_complete", {"comments": comments}))

    async def emit_clear_summary_comments_error(self) -> None:
        self.calls.append(("emit_clear_summary_comments_error", {}))


@pytest.fixture
def hook_service() -> HookService:
    return HookService()


@pytest.fixture
def fake_hook_service() -> FakeHookService:
    return FakeHookService()
