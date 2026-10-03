import pytest

from ai_review.config import settings
from ai_review.services.review.filter.tools import (
    filter_replies,
    get_answered_summary_comments,
    is_generated_comment,
)
from ai_review.services.vcs.types import ReviewCommentSchema, ReviewThreadSchema, ThreadKind


@pytest.mark.parametrize("field", ["inline_tag", "summary_tag", "inline_fallback_tag"])
def test_is_generated_comment_respects_configured_ai_tags(field: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.review, field, "<custom.ai+>")

    assert is_generated_comment("Finding <custom.ai+>")
    assert not is_generated_comment("Finding <custom.ai+>-extra")


@pytest.mark.parametrize(
    "body, expected",
    [
        ("", False),
        ("An ordinary comment", False),
        ("Why? #ai-review-inline-reply", False),
        ("Which tests? #ai-review-summary-reply", False),
        ("Finding #ai-review-inline-extra", False),
        ("Answer\n<!-- ai-review:inline-reply -->", True),
        ("Answer\n<!-- ai-review:summary-reply thread=t1 comment=c1 -->", True),
        ("> <!-- ai-review:inline-reply -->", False),
        ("> <!-- ai-review:summary-reply thread=t1 comment=c1 -->", False),
    ],
)
def test_is_generated_comment_distinguishes_user_comments_and_generated_footers(body: str, expected: bool):
    assert is_generated_comment(body) is expected


@pytest.mark.parametrize("tag", ["#ai-review-inline-reply", "#ai-review-summary-reply", "<custom.reply+>", ""])
def test_filter_replies_selects_exact_tag_and_preserves_generated_comments(tag: str):
    first = ReviewCommentSchema(id="first", body=f"First question {tag}")
    second = ReviewCommentSchema(id="second", body=f"Second question {tag}")
    comments = [
        first,
        ReviewCommentSchema(id="untagged", body="An ordinary comment"),
        ReviewCommentSchema(id="prefix", body=f"Question {tag}-extra"),
        ReviewCommentSchema(id="inline", body=f"Quoted {tag}\n{settings.review.inline_tag}"),
        ReviewCommentSchema(id="summary", body=f"Quoted {tag}\n{settings.review.summary_tag}"),
        ReviewCommentSchema(id="fallback", body=f"Quoted {tag}\n{settings.review.inline_fallback_tag}"),
        ReviewCommentSchema(id="inline-answer", body=f"Quoted {tag}\n<!-- ai-review:inline-reply -->"),
        ReviewCommentSchema(id="summary-answer", body=f"Quoted {tag}\n<!-- ai-review:summary-reply thread=t1 comment=c1 -->"),
        second,
    ]
    original = list(comments)

    assert filter_replies(comments, tag) == ([first, second] if tag else [])
    assert comments == original


def test_filter_replies_handles_empty_comments():
    assert filter_replies([], settings.review.inline_reply_tag) == []


def test_get_answered_summary_comments_collects_unique_references_across_threads():
    threads = [
        ReviewThreadSchema(id="empty", kind=ThreadKind.SUMMARY, comments=[]),
        ReviewThreadSchema(id="answer-thread", kind=ThreadKind.SUMMARY, comments=[
            ReviewCommentSchema(id=1, body="An ordinary comment"),
            ReviewCommentSchema(id=2, body="Answer\n<!-- ai-review:summary-reply thread=source%2Fone comment=7 -->"),
            ReviewCommentSchema(id=3, body="Duplicate\n<!-- ai-review:summary-reply thread=source%2Fone comment=7 -->"),
            ReviewCommentSchema(id=4, body="Answer\n<!-- ai-review:summary-reply thread=source%2Ftwo comment=7 -->"),
        ]),
        ReviewThreadSchema(id="another-answer-thread", kind=ThreadKind.SUMMARY, comments=[
            ReviewCommentSchema(id=1, body="Answer\n<!-- ai-review:summary-reply thread=source%2Fone comment=8 -->"),
        ]),
    ]

    assert get_answered_summary_comments(threads) == {
        ("source/one", "7"), ("source/two", "7"), ("source/one", "8"),
    }


def test_get_answered_summary_comments_ignores_quoted_and_incomplete_references():
    thread = ReviewThreadSchema(id="t1", kind=ThreadKind.SUMMARY, comments=[
        ReviewCommentSchema(id=1, body="> <!-- ai-review:summary-reply thread=t1 comment=c1 -->"),
        ReviewCommentSchema(id=2, body="<!-- ai-review:summary-reply thread=t1 -->"),
        ReviewCommentSchema(id=3, body="<!-- ai-review:summary-reply thread=t1 comment=c1 -->\nA new question"),
    ])

    assert get_answered_summary_comments([thread]) == set()
    assert get_answered_summary_comments([]) == set()
