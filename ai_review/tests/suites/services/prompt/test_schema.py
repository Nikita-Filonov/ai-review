import pytest

from ai_review.config import settings
from ai_review.services.prompt.schema import PromptContextSchema


def test_apply_format_inserts_variables() -> None:
    """Ensures simple string fields are correctly substituted into the template."""
    context = PromptContextSchema(
        review_title="My Review",
        review_author_username="nikita"
    )
    template = "Title: <<review_title>>, Author: @<<review_author_username>>"
    result = context.apply_format(template)
    assert result == "Title: My Review, Author: @nikita"


def test_apply_format_with_lists() -> None:
    """Ensures list fields are serialized as CSV strings and substituted into the template."""
    context = PromptContextSchema(
        review_reviewers=["Alice", "Bob"],
        review_reviewers_usernames=["alice", "bob"],
        labels=["bug", "feature"],
        changed_files=["a.py", "b.py"],
    )
    template = (
        "Reviewers: <<review_reviewers>>\n"
        "Usernames: <<review_reviewers_usernames>>\n"
        "Labels: <<labels>>\n"
        "Files: <<changed_files>>"
    )
    result = context.apply_format(template)
    assert "Alice, Bob" in result
    assert "alice, bob" in result
    assert "bug, feature" in result
    assert "a.py, b.py" in result


def test_apply_format_handles_missing_fields() -> None:
    """Ensures missing fields are replaced with empty strings."""
    context = PromptContextSchema()
    template = "Title: <<review_title>>, Reviewer: <<review_reviewer>>"
    result = context.apply_format(template)
    assert result == "Title: , Reviewer: "


def test_apply_format_unknown_placeholder_kept() -> None:
    """Ensures unknown placeholders remain unchanged in the template."""
    context = PromptContextSchema()
    template = "Unknown: <<does_not_exist>>"
    result = context.apply_format(template)
    assert result == "Unknown: <<does_not_exist>>"


def test_apply_format_multiple_occurrences() -> None:
    """Ensures multiple occurrences of the same placeholder are all replaced."""
    context = PromptContextSchema(review_title="My Review")
    template = "<<review_title>> again <<review_title>>"
    result = context.apply_format(template)
    assert result == "My Review again My Review"


def test_apply_format_override_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensures values from settings.prompt.context override local model values."""
    monkeypatch.setitem(settings.prompt.context, "review_title", "Overridden")
    context = PromptContextSchema(review_title="Local Value")
    template = "Title: <<review_title>>"
    result = context.apply_format(template)
    assert result == "Title: Overridden"


def test_apply_format_prefers_override_even_if_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensures overrides take precedence even if the override value is empty."""
    monkeypatch.setitem(settings.prompt.context, "review_title", "")
    context = PromptContextSchema(review_title="Local Value")
    template = "Title: <<review_title>>"
    result = context.apply_format(template)
    assert result == "Title: "


def test_apply_format_empty_list_serializes_to_empty_string() -> None:
    """Ensures empty lists are serialized to empty strings."""
    context = PromptContextSchema(labels=[])
    template = "Labels: <<labels>>"
    result = context.apply_format(template)
    assert result == "Labels: "


def test_apply_format_single_element_list() -> None:
    """Ensures lists with a single element are serialized without extra separators."""
    context = PromptContextSchema(labels=["bug"])
    template = "Labels: <<labels>>"
    result = context.apply_format(template)
    assert result == "Labels: bug"


def test_apply_format_list_with_spaces() -> None:
    """Ensures list items containing spaces are preserved in serialization."""
    context = PromptContextSchema(labels=[" bug ", " feature "])
    template = "Labels: <<labels>>"
    result = context.apply_format(template)
    assert result == "Labels:  bug ,  feature "


def test_apply_format_placeholder_case_sensitive() -> None:
    """Ensures placeholder matching is case-sensitive."""
    context = PromptContextSchema(review_title="My Review")
    template = "Title: <<Review_Title>>"
    result = context.apply_format(template)
    assert result == "Title: <<Review_Title>>"


def test_apply_format_override_with_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensures None in overrides is treated as an empty string."""
    monkeypatch.setitem(settings.prompt.context, "review_title", None)
    context = PromptContextSchema(review_title="Local Value")
    template = "Title: <<review_title>>"
    result = context.apply_format(template)
    assert result == "Title: "


def test_apply_format_placeholder_inside_word() -> None:
    """Ensures placeholders inside words are still replaced correctly."""
    context = PromptContextSchema(review_title="REV")
    template = "prefix-<<review_title>>-suffix"
    result = context.apply_format(template)
    assert result == "prefix-REV-suffix"


def test_apply_format_large_list() -> None:
    """Ensures large lists are serialized correctly without truncation."""
    context = PromptContextSchema(labels=[str(index) for index in range(100)])
    template = "Labels: <<labels>>"
    result = context.apply_format(template)
    assert result.startswith("Labels: 0, 1, 2")
    assert "99" in result
