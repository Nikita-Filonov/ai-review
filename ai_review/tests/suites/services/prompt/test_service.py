import pytest

from ai_review.config import settings
from ai_review.libs.config.prompt import PromptConfig
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.prompt.service import PromptService


@pytest.fixture(autouse=True)
def patch_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch methods of settings.prompt to return dummy values."""
    monkeypatch.setattr(PromptConfig, "load_inline", lambda self: ["GLOBAL_INLINE", "INLINE_PROMPT"])
    monkeypatch.setattr(PromptConfig, "load_context", lambda self: ["GLOBAL_CONTEXT", "CONTEXT_PROMPT"])
    monkeypatch.setattr(PromptConfig, "load_summary", lambda self: ["GLOBAL_SUMMARY", "SUMMARY_PROMPT"])
    monkeypatch.setattr(PromptConfig, "load_system_inline", lambda self: ["SYS_INLINE_A", "SYS_INLINE_B"])
    monkeypatch.setattr(PromptConfig, "load_system_context", lambda self: ["SYS_CONTEXT_A", "SYS_CONTEXT_B"])
    monkeypatch.setattr(PromptConfig, "load_system_summary", lambda self: ["SYS_SUMMARY_A", "SYS_SUMMARY_B"])


@pytest.fixture
def dummy_context() -> PromptContextSchema:
    """Builds a context object that reflects the new unified review schema."""
    return PromptContextSchema(
        review_title="Fix login bug",
        review_description="Some description",
        review_author_name="Nikita",
        review_author_username="nikita.filonov",
        review_reviewers=["Alice", "Bob"],
        review_reviewers_usernames=["alice", "bob"],
        review_assignees=["Charlie"],
        review_assignees_usernames=["charlie"],
        source_branch="feature/login-fix",
        target_branch="main",
        labels=["bug", "critical"],
        changed_files=["foo.py", "bar.py"],
    )


def test_build_inline_request_includes_prompts_and_diff(dummy_context: PromptContextSchema) -> None:
    diff = DiffFileSchema(file="foo.py", diff="+ added line\n- removed line")
    result = PromptService.build_inline_request(diff, dummy_context)

    assert "GLOBAL_INLINE" in result
    assert "INLINE_PROMPT" in result
    assert "# File: foo.py" in result
    assert "+ added line" in result
    assert "- removed line" in result


def test_build_summary_request_includes_prompts_and_diffs(dummy_context: PromptContextSchema) -> None:
    diffs = [
        DiffFileSchema(file="a.py", diff="+ foo"),
        DiffFileSchema(file="b.py", diff="- bar"),
    ]
    result = PromptService.build_summary_request(diffs, dummy_context)

    assert "GLOBAL_SUMMARY" in result
    assert "SUMMARY_PROMPT" in result
    assert "# File: a.py" in result
    assert "# File: b.py" in result
    assert "+ foo" in result
    assert "- bar" in result


def test_build_summary_request_empty_list(dummy_context: PromptContextSchema) -> None:
    """Empty diffs list should still produce valid prompt with no diff content."""
    result = PromptService.build_summary_request([], dummy_context)

    assert "GLOBAL_SUMMARY" in result
    assert "SUMMARY_PROMPT" in result
    assert "## Changes" in result
    assert result.strip().endswith("## Changes")


def test_build_context_request_includes_prompts_and_diffs(dummy_context: PromptContextSchema) -> None:
    diffs = [
        DiffFileSchema(file="a.py", diff="+ foo"),
        DiffFileSchema(file="b.py", diff="- bar"),
    ]
    result = PromptService.build_context_request(diffs, dummy_context)

    assert "GLOBAL_CONTEXT" in result
    assert "CONTEXT_PROMPT" in result
    assert "# File: a.py" in result
    assert "# File: b.py" in result
    assert "+ foo" in result
    assert "- bar" in result


def test_build_system_inline_request_returns_joined_prompts(dummy_context: PromptContextSchema) -> None:
    result = PromptService.build_system_inline_request(dummy_context)
    assert result == "SYS_INLINE_A\n\nSYS_INLINE_B".replace("SYS_INLINE_A", "SYS_INLINE_A")


def test_build_system_context_request_returns_joined_prompts(dummy_context: PromptContextSchema) -> None:
    result = PromptService.build_system_context_request(dummy_context)
    assert result == "SYS_CONTEXT_A\n\nSYS_CONTEXT_B"


def test_build_system_summary_request_returns_joined_prompts(dummy_context: PromptContextSchema) -> None:
    result = PromptService.build_system_summary_request(dummy_context)
    assert result == "SYS_SUMMARY_A\n\nSYS_SUMMARY_B"


def test_build_system_inline_request_empty(
        monkeypatch: pytest.MonkeyPatch,
        dummy_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(PromptConfig, "load_system_inline", lambda self: [])
    result = PromptService.build_system_inline_request(dummy_context)
    assert result == ""


def test_build_system_context_request_empty(
        monkeypatch: pytest.MonkeyPatch,
        dummy_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(PromptConfig, "load_system_context", lambda self: [])
    result = PromptService.build_system_context_request(dummy_context)
    assert result == ""


def test_build_system_summary_request_empty(
        monkeypatch: pytest.MonkeyPatch,
        dummy_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(PromptConfig, "load_system_summary", lambda self: [])
    result = PromptService.build_system_summary_request(dummy_context)
    assert result == ""


def test_diff_placeholders_are_not_replaced(dummy_context: PromptContextSchema) -> None:
    diffs = [DiffFileSchema(file="x.py", diff='print("<<review_title>>")')]
    result = PromptService.build_summary_request(diffs, dummy_context)

    assert "<<review_title>>" in result
    assert "Fix login bug" not in result


def test_prepare_prompt_basic_substitution(dummy_context: PromptContextSchema) -> None:
    prompts = ["Hello", "MR title: <<review_title>>"]
    result = PromptService.prepare_prompt(prompts, dummy_context)

    assert "Hello" in result
    assert "MR title: Fix login bug" in result


def test_prepare_prompt_applies_normalization(
        monkeypatch: pytest.MonkeyPatch,
        dummy_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(settings.prompt, "normalize_prompts", True)
    prompts = ["Line with space   ", "", "", "Next line"]
    result = PromptService.prepare_prompt(prompts, dummy_context)

    assert "Line with space" in result
    assert "Next line" in result
    assert "\n\n\n" not in result


def test_prepare_prompt_skips_normalization(
        monkeypatch: pytest.MonkeyPatch,
        dummy_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(settings.prompt, "normalize_prompts", False)
    prompts = ["Line with space   ", "", "", "Next line"]
    result = PromptService.prepare_prompt(prompts, dummy_context)

    assert "Line with space   " in result
    assert "\n\n\n" in result
