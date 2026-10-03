import pytest

from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.review.internal.summary_reply.tools import get_summary_reply_reference


@pytest.mark.parametrize(
    ("thread_id", "comment_id"),
    [(10, 1), ("discussion-123", "comment-42"), ("a/b: c", "x -->\n雪%")],
)
def test_reply_reference_preserves_identifiers(thread_id: str | int, comment_id: str | int):
    body = SummaryCommentReplySchema(text="Answer").body_for_request(thread_id, comment_id)

    assert get_summary_reply_reference(body) == (str(thread_id), str(comment_id))
    assert body.count("-->") == 1


@pytest.mark.parametrize(
    "body",
    [
        "Answer #ai-review-summary",
        "<!-- ai-review:summary-reply thread=t1 -->",
        "<!-- ai-review:summary-reply thread=t1 comment= -->",
        "> <!-- ai-review:summary-reply thread=t1 comment=c1 -->",
        "```\n<!-- ai-review:summary-reply thread=t1 comment=c1 -->\n```",
        "<!-- ai-review:summary-reply thread=t1 comment=c1 -->\nQuestion",
    ],
)
def test_only_complete_footer_marks_a_reply(body: str):
    assert get_summary_reply_reference(body) is None


def test_reply_reference_allows_trailing_whitespace():
    body = "Answer\n\n<!-- ai-review:summary-reply thread=t1 comment=c1 -->\n\t"
    assert get_summary_reply_reference(body) == ("t1", "c1")
