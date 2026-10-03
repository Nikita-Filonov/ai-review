import pytest

from ai_review.config import settings
from ai_review.services.review.filter.service import ReviewFilterService
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import ReviewCommentSchema, ReviewThreadSchema, ThreadKind


@pytest.mark.parametrize(
    ("bodies", "expected"),
    [
        ([], False),
        (["Review #ai-review-inline"], False),
        (["Question #ai-review-inline-reply"], True),
        (["Question #ai-review-inline-reply", "Answer #ai-review-inline"], False),
        (["Question #ai-review-inline-reply", "Untagged follow-up"], False),
        (["Answer #ai-review-inline", "Follow-up #ai-review-inline-reply"], True),
        (["Question #ai-review-inline-reply-extra"], False),
        (["Bot quotes #ai-review-inline-reply\n\n#ai-review-inline"], False),
    ],
)
def test_filter_inline_threads_uses_only_latest_comment(
        bodies: list[str],
        expected: bool,
        review_filter_service: ReviewFilterService,
):
    thread = ReviewThreadSchema(
        id="thread-1",
        kind=ThreadKind.INLINE,
        file="main.py",
        comments=[ReviewCommentSchema(id=index, body=body) for index, body in enumerate(bodies)],
    )

    assert review_filter_service.filter_inline_threads([thread]) == ([thread] if expected else [])


@pytest.mark.parametrize("tag", ["", "<request.reply+>"])
def test_filter_inline_threads_respects_configured_tag(
        tag: str,
        monkeypatch: pytest.MonkeyPatch,
        review_filter_service: ReviewFilterService,
):
    monkeypatch.setattr(settings.review, "inline_reply_tag", tag)
    thread = ReviewThreadSchema(
        id="thread-1",
        kind=ThreadKind.INLINE,
        comments=[ReviewCommentSchema(id=1, body="Question <request.reply+>")],
    )

    assert review_filter_service.filter_inline_threads([thread]) == ([thread] if tag else [])


@pytest.mark.parametrize(
    ("bodies", "expected"),
    [
        ([], False),
        (["Summary #ai-review-summary"], False),
        (["Why? #ai-review-summary-reply"], True),
        (["Why? #ai-review-summary-reply-extra"], False),
        (["Why? #ai-review-summary-reply", "Untagged follow-up"], False),
        (["Why? #ai-review-summary-reply", "Answer #ai-review-summary"], False),
        (["Answer #ai-review-summary", "Follow-up #ai-review-summary-reply"], True),
        (["Bot quotes #ai-review-summary-reply\n\n#ai-review-summary"], False),
    ],
)
def test_filter_summary_threads_uses_latest_request(
        bodies: list[str],
        expected: bool,
        review_filter_service: ReviewFilterService,
):
    thread = ReviewThreadSchema(
        id="t1", kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(id=index, body=body) for index, body in enumerate(bodies)],
    )

    assert review_filter_service.filter_summary_threads([thread]) == ([thread] if expected else [])


@pytest.mark.parametrize("tag", ["", "<request.summary+>"])
def test_filter_summary_threads_respects_configured_tag(
        tag: str,
        monkeypatch: pytest.MonkeyPatch,
        review_filter_service: ReviewFilterService,
):
    monkeypatch.setattr(settings.review, "summary_reply_tag", tag)
    thread = ReviewThreadSchema(
        id="t1", kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(id=1, body="Question <request.summary+>")],
    )

    assert review_filter_service.filter_summary_threads([thread]) == ([thread] if tag else [])


def test_summary_acknowledgement_is_scoped_to_thread_and_comment(
        review_filter_service: ReviewFilterService,
):
    requests = [
        ReviewThreadSchema(
            id=thread_id, kind=ThreadKind.SUMMARY,
            comments=[ReviewCommentSchema(id=1, body="Why? #ai-review-summary-reply")],
        )
        for thread_id in [10, 20]
    ]
    # A separate reply acknowledges string IDs, as persisted by an earlier process.
    answer = ReviewThreadSchema(
        id=30, kind=ThreadKind.SUMMARY,
        comments=[ReviewCommentSchema(
            id=1, body=SummaryCommentReplySchema(text="Answer").body_for_request("10", "1"),
        )],
    )
    threads = [answer, *requests]

    assert review_filter_service.filter_summary_threads(threads) == [requests[1]]

    requests[0].comments.append(ReviewCommentSchema(id=2, body="Follow-up #ai-review-summary-reply"))
    assert review_filter_service.filter_summary_threads(threads) == requests


def test_summary_reply_marker_prevents_self_reply_after_tag_change(
        monkeypatch: pytest.MonkeyPatch,
        review_filter_service: ReviewFilterService,
):
    body = SummaryCommentReplySchema(text="Quoted #ai-review-summary-reply").body_for_request("t1", "c1")
    monkeypatch.setattr(settings.review, "summary_tag", "#new-summary-tag")
    threads = [ReviewThreadSchema(
        id="reply", kind=ThreadKind.SUMMARY, comments=[ReviewCommentSchema(id="c2", body=body)],
    )]

    assert review_filter_service.filter_summary_threads(threads) == []


@pytest.mark.parametrize(
    "method, expected_ids",
    [
        ("filter_inline_comments", ["1", "3"]),
        ("filter_summary_comments", ["4"]),
        ("filter_clearable_summary_comments", ["4", "6", "7"]),
        ("filter_inline_replies", ["2"]),
        ("filter_summary_replies", ["5"]),
        ("filter_generated_inline_replies", ["3"]),
    ],
)
def test_filters_distinguish_findings_replies_and_generated_answers(
        method: str,
        expected_ids: list[str],
        review_filter_service: ReviewFilterService,
):
    comments = [
        ReviewCommentSchema(id="1", body="Finding #ai-review-inline"),
        ReviewCommentSchema(id="2", body="Why? #ai-review-inline-reply"),
        ReviewCommentSchema(id="3", body=InlineCommentReplySchema(message="Because").body_with_tag),
        ReviewCommentSchema(id="4", body="Overview #ai-review-summary"),
        ReviewCommentSchema(id="5", body="Which tests? #ai-review-summary-reply"),
        ReviewCommentSchema(id="6", body=SummaryCommentReplySchema(text="Edge cases").body_for_request("t", "5")),
        ReviewCommentSchema(id="7", body="Fallback #ai-review-inline-fallback"),
        ReviewCommentSchema(id="8", body="An unrelated comment"),
    ]

    selected = getattr(review_filter_service, method)(comments)

    assert [comment.id for comment in selected] == expected_ids
    assert [comment.id for comment in comments] == [str(index) for index in range(1, 9)]


@pytest.mark.parametrize(
    "method, config_field",
    [("filter_inline_replies", "inline_reply_tag"), ("filter_summary_replies", "summary_reply_tag")],
)
@pytest.mark.parametrize("tag", ["", "<custom.reply+>"])
def test_reply_filters_use_settings(
        method: str,
        config_field: str,
        tag: str,
        monkeypatch: pytest.MonkeyPatch,
        review_filter_service: ReviewFilterService,
):
    monkeypatch.setattr(settings.review, config_field, tag)
    reply = ReviewCommentSchema(id="reply", body="Question <custom.reply+>")
    comments = [reply, ReviewCommentSchema(id="prefix", body="Question <custom.reply+>-extra")]

    assert getattr(review_filter_service, method)(comments) == ([reply] if tag else [])


@pytest.mark.parametrize(
    "method, tag",
    [("filter_inline_replies", "#ai-review-inline-reply"), ("filter_summary_replies", "#ai-review-summary-reply")],
)
def test_reply_filters_preserve_generated_answers_after_ai_tag_changes(
        method: str,
        tag: str,
        monkeypatch: pytest.MonkeyPatch,
        review_filter_service: ReviewFilterService,
):
    reply = ReviewCommentSchema(id="reply", body=f"Question {tag}")
    comments = [
        reply,
        ReviewCommentSchema(id="inline", body=InlineCommentReplySchema(message=f"Quoting {tag}").body_with_tag),
        ReviewCommentSchema(id="summary", body=SummaryCommentReplySchema(text=f"Quoting {tag}").body_for_request("t", "q")),
    ]
    monkeypatch.setattr(settings.review, "inline_tag", "#new-inline")
    monkeypatch.setattr(settings.review, "summary_tag", "#new-summary")

    assert getattr(review_filter_service, method)(comments) == [reply]


def test_exclude_duplicate_comments_matches_note_identity(
        review_filter_service: ReviewFilterService,
):
    selected = [ReviewCommentSchema(id=42, body="same note")]
    duplicate = ReviewCommentSchema(id="42", body="same note")
    different_body = ReviewCommentSchema(id="42", body="different note")
    different_id = ReviewCommentSchema(id=43, body="same note")

    assert review_filter_service.exclude_duplicate_comments(
        [duplicate, different_body, different_id], selected,
    ) == [different_body, different_id]
