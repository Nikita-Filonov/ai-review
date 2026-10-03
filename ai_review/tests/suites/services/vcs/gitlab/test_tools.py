import pytest

from ai_review.clients.gitlab.mr.schema.draft_notes import GitLabDraftNoteSchema
from ai_review.config import settings
from ai_review.services.vcs.gitlab.tools import filter_ai_review_drafts


def _make_draft(draft_id: int, note: str) -> GitLabDraftNoteSchema:
    return GitLabDraftNoteSchema(id=draft_id, note=note)


def test_filter_ai_review_drafts_matches_every_configured_tag(
        monkeypatch: pytest.MonkeyPatch,
):
    tags_by_setting = {
        "inline_tag": "<inline>",
        "inline_reply_tag": "<inline-reply>",
        "inline_fallback_tag": "<inline-fallback>",
        "summary_tag": "<summary>",
        "summary_reply_tag": "<summary-reply>",
    }
    for setting, tag in tags_by_setting.items():
        monkeypatch.setattr(settings.review, setting, tag)

    drafts = [
        _make_draft(index, f"Draft comment {tag}")
        for index, tag in enumerate(tags_by_setting.values(), start=1)
    ]

    assert filter_ai_review_drafts(drafts) == drafts


def test_filter_ai_review_drafts_excludes_unrelated_drafts():
    drafts = [
        _make_draft(1, "Human review draft"),
        _make_draft(2, "Draft from another integration #other-tool"),
    ]

    assert filter_ai_review_drafts(drafts) == []


def test_filter_ai_review_drafts_filters_mixed_list_without_reordering():
    inline = _make_draft(1, f"Inline comment {settings.review.inline_tag}")
    manual = _make_draft(2, "Human review draft")
    summary = _make_draft(3, f"Summary comment {settings.review.summary_tag}")
    other = _make_draft(4, "Draft from another integration #other-tool")

    assert filter_ai_review_drafts([inline, manual, summary, other]) == [inline, summary]


def test_filter_ai_review_drafts_ignores_empty_tags(monkeypatch: pytest.MonkeyPatch):
    for setting in (
            "inline_tag",
            "inline_reply_tag",
            "inline_fallback_tag",
            "summary_tag",
            "summary_reply_tag",
    ):
        monkeypatch.setattr(settings.review, setting, "")

    assert filter_ai_review_drafts([_make_draft(1, "Any draft")]) == []


def test_filter_ai_review_drafts_returns_empty_list_for_empty_input():
    assert filter_ai_review_drafts([]) == []
