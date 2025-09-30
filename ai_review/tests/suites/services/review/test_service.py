import pytest

from ai_review.services.review.service import ReviewService
from ai_review.tests.fixtures.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.cost import FakeCostService
from ai_review.tests.fixtures.diff import FakeDiffService
from ai_review.tests.fixtures.git import FakeGitService
from ai_review.tests.fixtures.llm import FakeLLMClient
from ai_review.tests.fixtures.prompt import FakePromptService
from ai_review.tests.fixtures.review.inline import FakeInlineCommentService
from ai_review.tests.fixtures.review.summary import FakeSummaryCommentService
from ai_review.tests.fixtures.vcs import FakeVCSClient


@pytest.fixture
def review_service(
        monkeypatch: pytest.MonkeyPatch,
        fake_vcs_client: FakeVCSClient,
        fake_llm_client: FakeLLMClient,
        fake_git_service: FakeGitService,
        fake_diff_service: FakeDiffService,
        fake_cost_service: FakeCostService,
        fake_prompt_service: FakePromptService,
        fake_artifacts_service: FakeArtifactsService,
        fake_inline_comment_service: FakeInlineCommentService,
        fake_summary_comment_service: FakeSummaryCommentService,
):
    monkeypatch.setattr("ai_review.services.review.service.get_llm_client", lambda: fake_llm_client)
    monkeypatch.setattr("ai_review.services.review.service.get_vcs_client", lambda: fake_vcs_client)
    monkeypatch.setattr("ai_review.services.review.service.GitService", lambda: fake_git_service)
    monkeypatch.setattr("ai_review.services.review.service.DiffService", lambda: fake_diff_service)
    monkeypatch.setattr("ai_review.services.review.service.PromptService", lambda: fake_prompt_service)
    monkeypatch.setattr("ai_review.services.review.service.InlineCommentService", lambda: fake_inline_comment_service)
    monkeypatch.setattr("ai_review.services.review.service.SummaryCommentService", lambda: fake_summary_comment_service)
    monkeypatch.setattr("ai_review.services.review.service.ArtifactsService", lambda: fake_artifacts_service)
    monkeypatch.setattr("ai_review.services.review.service.CostService", lambda: fake_cost_service)
    return ReviewService()


@pytest.mark.asyncio
async def test_run_inline_review_happy_path(
        review_service: ReviewService,
        fake_vcs_client: FakeVCSClient,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        fake_git_service: FakeGitService,
        fake_diff_service: FakeDiffService,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
):
    """Should perform inline review for changed files and create inline comments via VCS."""
    fake_git_service.responses["get_diff_for_file"] = "FAKE_DIFF"

    await review_service.run_inline_review()

    vcs_calls = [c[0] for c in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert "create_inline_comment" in vcs_calls

    assert (
               "get_diff_for_file",
               {"base_sha": "A", "head_sha": "B", "file": "file.py", "unified": 3}
           ) in fake_git_service.calls
    assert any(call[0] == "render_file" for call in fake_diff_service.calls)

    assert any(call[0] == "build_inline_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "chat" for call in fake_llm_client.calls)

    assert len(fake_cost_service.reports) == 1
    assert any(call[0] == "save_llm_interaction" for call in fake_artifacts_service.calls)


@pytest.mark.asyncio
async def test_run_inline_review_skips_when_no_diff(
        review_service: ReviewService,
        fake_vcs_client: FakeVCSClient,
        fake_git_service: FakeGitService,
        fake_llm_client: FakeLLMClient,
):
    """Should skip inline review when no diffs exist."""
    fake_git_service.responses["get_diff_for_file"] = ""

    await review_service.run_inline_review()

    assert not any(call[0] == "chat" for call in fake_llm_client.calls)
    assert not any(call[0] == "create_inline_comment" for call in fake_vcs_client.calls)


@pytest.mark.asyncio
async def test_run_context_review_happy_path(
        review_service: ReviewService,
        fake_vcs_client: FakeVCSClient,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        fake_diff_service: FakeDiffService,
):
    """Should perform context review and post inline comments based on rendered files."""
    await review_service.run_context_review()

    vcs_calls = [c[0] for c in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert "create_inline_comment" in vcs_calls

    assert any(call[0] == "render_files" for call in fake_diff_service.calls)
    assert any(call[0] == "build_context_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "chat" for call in fake_llm_client.calls)


@pytest.mark.asyncio
async def test_run_summary_review_happy_path(
        review_service: ReviewService,
        fake_vcs_client: FakeVCSClient,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        fake_diff_service: FakeDiffService,
):
    """Should perform summary review and post a single summary comment."""
    await review_service.run_summary_review()

    vcs_calls = [c[0] for c in fake_vcs_client.calls]
    assert "get_review_info" in vcs_calls
    assert "create_general_comment" in vcs_calls

    assert any(call[0] == "render_files" for call in fake_diff_service.calls)
    assert any(call[0] == "build_summary_request" for call in fake_prompt_service.calls)
    assert any(call[0] == "chat" for call in fake_llm_client.calls)
