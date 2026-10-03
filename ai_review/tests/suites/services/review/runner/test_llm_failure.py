import pytest

from ai_review.tests.fixtures.services.git import FakeGitService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_direct_llm_gateway import FakeReviewDirectLLMGateway


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "runner_fixture, parser_attribute",
    [
        ("inline_review_runner", "inline_comment"),
        ("context_review_runner", "inline_comment"),
        ("summary_review_runner", "summary_comment"),
        ("inline_reply_review_runner", "inline_comment_reply"),
        ("summary_reply_review_runner", "summary_comment_reply"),
    ],
)
async def test_failed_llm_call_skips_parsing_and_posting(
        runner_fixture: str,
        parser_attribute: str,
        request: pytest.FixtureRequest,
        fake_git_service: FakeGitService,
        fake_review_direct_llm_gateway: FakeReviewDirectLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    runner = request.getfixturevalue(runner_fixture)
    fake_git_service.responses["get_diff_for_file"] = "FAKE_DIFF"
    fake_review_direct_llm_gateway.responses["ask"] = None
    fake_review_comment_gateway.responses["get_inline_comments"] = []
    fake_review_comment_gateway.responses["get_summary_comments"] = []

    await runner.run()

    assert any(call[0] == "ask" for call in fake_review_direct_llm_gateway.calls)
    assert getattr(runner, parser_attribute).calls == []
    assert not any(call[0].startswith("process_") for call in fake_review_comment_gateway.calls)
