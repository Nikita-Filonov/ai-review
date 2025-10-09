import pytest

from ai_review.services.review.runner.inline import InlineReviewRunner
from ai_review.services.vcs.types import ReviewInfoSchema
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.diff import FakeDiffService
from ai_review.tests.fixtures.services.git import FakeGitService
from ai_review.tests.fixtures.services.prompt import FakePromptService
from ai_review.tests.fixtures.services.review.gateway.review_comment_gateway import FakeReviewCommentGateway
from ai_review.tests.fixtures.services.review.gateway.review_llm_gateway import FakeReviewLLMGateway
from ai_review.tests.fixtures.services.review.internal.inline import FakeInlineCommentService
from ai_review.tests.fixtures.services.review.internal.policy import FakeReviewPolicyService
from ai_review.tests.fixtures.services.vcs import FakeVCSClient


@pytest.mark.asyncio
async def test_run_happy_path(
        inline_review_runner: InlineReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_git_service: FakeGitService,
        fake_diff_service: FakeDiffService,
        fake_cost_service: FakeCostService,
        fake_prompt_service: FakePromptService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_policy_service: FakeReviewPolicyService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should process all changed files, call LLM and post inline comments."""
    fake_git_service.responses["get_diff_for_file"] = "FAKE_DIFF"

    await inline_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls

    git_calls = [call[0] for call in fake_git_service.calls]
    assert any(call == "get_diff_for_file" for call in git_calls)

    assert any(call[0] == "render_file" for call in fake_diff_service.calls)
    assert any(call[0] == "apply_for_files" for call in fake_review_policy_service.calls)
    assert any(call[0] == "build_inline_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert any(call[0] == "process_inline_comments" for call in fake_review_comment_gateway.calls)

    assert any(call[0] == "aggregate" for call in fake_cost_service.calls)


@pytest.mark.asyncio
async def test_run_skips_when_existing_comments(
        inline_review_runner: InlineReviewRunner,
        fake_vcs_client: FakeVCSClient,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should skip review if there are already existing inline comments."""
    fake_review_comment_gateway.responses["has_existing_inline_comments"] = True

    await inline_review_runner.run()

    vcs_calls = [call[0] for call in fake_vcs_client.calls]
    assert vcs_calls == []
    assert not any(call[0] == "ask" for call in fake_review_llm_gateway.calls)


@pytest.mark.asyncio
async def test_process_file_skips_when_no_diff(
        inline_review_runner: InlineReviewRunner,
        fake_git_service: FakeGitService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_comment_gateway: FakeReviewCommentGateway,
):
    """Should skip processing file if no diff found."""
    fake_git_service.responses["get_diff_for_file"] = ""

    review_info = ReviewInfoSchema(base_sha="A", head_sha="B")
    await inline_review_runner.process_file("file.py", review_info)

    assert not any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert not any(call[0] == "process_inline_comments" for call in fake_review_comment_gateway.calls)


@pytest.mark.asyncio
async def test_process_file_skips_when_no_comments_after_llm(
        inline_review_runner: InlineReviewRunner,
        fake_git_service: FakeGitService,
        fake_review_llm_gateway: FakeReviewLLMGateway,
        fake_review_policy_service: FakeReviewPolicyService,
        fake_review_comment_gateway: FakeReviewCommentGateway,
        fake_inline_comment_service: FakeInlineCommentService,
):
    """Should not post comments if model output produces no inline comments."""
    fake_git_service.responses["get_diff_for_file"] = "SOME_DIFF"
    fake_inline_comment_service.comments = []

    review_info = ReviewInfoSchema(base_sha="A", head_sha="B")
    await inline_review_runner.process_file("file.py", review_info)

    assert any(call[0] == "ask" for call in fake_review_llm_gateway.calls)
    assert any(call[0] == "apply_for_inline_comments" for call in fake_review_policy_service.calls)
    assert not any(call[0] == "process_inline_comments" for call in fake_review_comment_gateway.calls)
