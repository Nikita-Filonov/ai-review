import pytest

from ai_review.config import settings
from ai_review.libs.config.prompt import PromptConfig
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.prompt.service import PromptService
from ai_review.services.vcs.types import ReviewThreadSchema, ThreadKind, ReviewCommentSchema


@pytest.mark.usefixtures("fake_prompts")
def test_build_inline_request_includes_prompts_and_diff(fake_prompt_context: PromptContextSchema) -> None:
    diff = DiffFileSchema(file="foo.py", diff="+ added line\n- removed line")
    result = PromptService.build_inline_request(diff, fake_prompt_context)

    assert "GLOBAL_INLINE" in result
    assert "INLINE_PROMPT" in result
    assert "# File: foo.py" in result
    assert "+ added line" in result
    assert "- removed line" in result


@pytest.mark.usefixtures("fake_prompts")
def test_build_summary_request_includes_prompts_and_diffs(fake_prompt_context: PromptContextSchema) -> None:
    diffs = [
        DiffFileSchema(file="a.py", diff="+ foo"),
        DiffFileSchema(file="b.py", diff="- bar"),
    ]
    result = PromptService.build_summary_request(diffs, fake_prompt_context)

    assert "GLOBAL_SUMMARY" in result
    assert "SUMMARY_PROMPT" in result
    assert "# File: a.py" in result
    assert "# File: b.py" in result
    assert "+ foo" in result
    assert "- bar" in result


@pytest.mark.usefixtures("fake_prompts")
def test_build_summary_request_empty_list(fake_prompt_context: PromptContextSchema) -> None:
    """Empty diffs list should still produce valid prompt with no diff content."""
    result = PromptService.build_summary_request([], fake_prompt_context)

    assert "GLOBAL_SUMMARY" in result
    assert "SUMMARY_PROMPT" in result
    assert "## Changes" in result
    assert result.strip().endswith("## Changes")


@pytest.mark.usefixtures("fake_prompts")
def test_build_context_request_includes_prompts_and_diffs(fake_prompt_context: PromptContextSchema) -> None:
    diffs = [
        DiffFileSchema(file="a.py", diff="+ foo"),
        DiffFileSchema(file="b.py", diff="- bar"),
    ]
    result = PromptService.build_context_request(diffs, fake_prompt_context)

    assert "GLOBAL_CONTEXT" in result
    assert "CONTEXT_PROMPT" in result
    assert "# File: a.py" in result
    assert "# File: b.py" in result
    assert "+ foo" in result
    assert "- bar" in result


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_inline_request_returns_joined_prompts(fake_prompt_context: PromptContextSchema) -> None:
    result = PromptService.build_system_inline_request(fake_prompt_context)
    assert result == "SYS_INLINE_A\n\nSYS_INLINE_B".replace("SYS_INLINE_A", "SYS_INLINE_A")


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_context_request_returns_joined_prompts(fake_prompt_context: PromptContextSchema) -> None:
    result = PromptService.build_system_context_request(fake_prompt_context)
    assert result == "SYS_CONTEXT_A\n\nSYS_CONTEXT_B"


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_summary_request_returns_joined_prompts(fake_prompt_context: PromptContextSchema) -> None:
    result = PromptService.build_system_summary_request(fake_prompt_context)
    assert result == "SYS_SUMMARY_A\n\nSYS_SUMMARY_B"


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_inline_request_empty(
        monkeypatch: pytest.MonkeyPatch,
        fake_prompt_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(PromptConfig, "load_system_inline", lambda self: [])
    result = PromptService.build_system_inline_request(fake_prompt_context)
    assert result == ""


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_context_request_empty(
        monkeypatch: pytest.MonkeyPatch,
        fake_prompt_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(PromptConfig, "load_system_context", lambda self: [])
    result = PromptService.build_system_context_request(fake_prompt_context)
    assert result == ""


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_summary_request_empty(
        monkeypatch: pytest.MonkeyPatch,
        fake_prompt_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(PromptConfig, "load_system_summary", lambda self: [])
    result = PromptService.build_system_summary_request(fake_prompt_context)
    assert result == ""


@pytest.mark.usefixtures("fake_prompts")
def test_diff_placeholders_are_not_replaced(fake_prompt_context: PromptContextSchema) -> None:
    diffs = [DiffFileSchema(file="x.py", diff='print("<<review_title>>")')]
    result = PromptService.build_summary_request(diffs, fake_prompt_context)

    assert "<<review_title>>" in result
    assert "Fix login bug" not in result


@pytest.mark.usefixtures("fake_prompts")
def test_prepare_prompt_basic_substitution(fake_prompt_context: PromptContextSchema) -> None:
    prompts = ["Hello", "MR title: <<review_title>>"]
    result = PromptService.prepare_prompt(prompts, fake_prompt_context)

    assert "Hello" in result
    assert "MR title: Fix login bug" in result


@pytest.mark.usefixtures("fake_prompts")
def test_prepare_prompt_applies_normalization(
        monkeypatch: pytest.MonkeyPatch,
        fake_prompt_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(settings.prompt, "normalize_prompts", True)
    prompts = ["Line with space   ", "", "", "Next line"]
    result = PromptService.prepare_prompt(prompts, fake_prompt_context)

    assert "Line with space" in result
    assert "Next line" in result
    assert "\n\n\n" not in result


@pytest.mark.usefixtures("fake_prompts")
def test_prepare_prompt_skips_normalization(
        monkeypatch: pytest.MonkeyPatch,
        fake_prompt_context: PromptContextSchema
) -> None:
    monkeypatch.setattr(settings.prompt, "normalize_prompts", False)
    prompts = ["Line with space   ", "", "", "Next line"]
    result = PromptService.prepare_prompt(prompts, fake_prompt_context)

    assert "Line with space   " in result
    assert "\n\n\n" in result


@pytest.mark.usefixtures("fake_prompts")
def test_build_inline_reply_request_includes_conversation_and_diff(fake_prompt_context: PromptContextSchema) -> None:
    diff = DiffFileSchema(file="foo.py", diff="+ added\n- removed")
    thread = ReviewThreadSchema(
        id="t1",
        kind=ThreadKind.INLINE,
        file="foo.py",
        line=10,
        comments=[
            ReviewCommentSchema(id=1, body="Initial comment"),
            ReviewCommentSchema(id=2, body="Follow-up"),
        ],
    )

    result = PromptService.build_inline_reply_request(diff, thread, fake_prompt_context)

    assert "INLINE_REPLY_A" in result
    assert "INLINE_REPLY_B" in result
    assert "## Conversation" in result
    assert "Initial comment" in result
    assert "Follow-up" in result
    assert "## Diff" in result
    assert "# File: foo.py" in result
    assert "+ added" in result


@pytest.mark.usefixtures("fake_prompts")
def test_build_summary_reply_request_includes_conversation_and_changes(
        fake_prompt_context: PromptContextSchema
) -> None:
    diffs = [DiffFileSchema(file="a.py", diff="+ foo")]
    thread = ReviewThreadSchema(
        id="t2",
        kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(id=1, body="Overall feedback")],
    )

    result = PromptService.build_summary_reply_request(diffs, thread, fake_prompt_context)

    assert "SUMMARY_REPLY_A" in result
    assert "SUMMARY_REPLY_B" in result
    assert "## Conversation" in result
    assert "Overall feedback" in result
    assert "## Changes" in result
    assert "+ foo" in result


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_inline_reply_request_returns_joined_prompts(fake_prompt_context: PromptContextSchema) -> None:
    result = PromptService.build_system_inline_reply_request(fake_prompt_context)
    assert result == "SYS_INLINE_REPLY_A\n\nSYS_INLINE_REPLY_B"


@pytest.mark.usefixtures("fake_prompts")
def test_build_system_summary_reply_request_returns_joined_prompts(fake_prompt_context: PromptContextSchema) -> None:
    result = PromptService.build_system_summary_reply_request(fake_prompt_context)
    assert result == "SYS_SUMMARY_REPLY_A\n\nSYS_SUMMARY_REPLY_B"
