from ai_review.config import settings
from ai_review.libs.text import contains_tag
from ai_review.services.review.internal.inline_reply.tools import is_inline_reply
from ai_review.services.review.internal.summary_reply.tools import get_summary_reply_reference
from ai_review.services.vcs.types import ReviewCommentSchema, ReviewThreadSchema


def is_generated_comment(body: str) -> bool:
    tags = (settings.review.inline_tag, settings.review.summary_tag, settings.review.inline_fallback_tag)
    return (
        any(contains_tag(body, tag) for tag in tags)
        or is_inline_reply(body)
        or get_summary_reply_reference(body) is not None
    )


def filter_replies(comments: list[ReviewCommentSchema], tag: str) -> list[ReviewCommentSchema]:
    return [
        comment for comment in comments
        if contains_tag(comment.body, tag) and not is_generated_comment(comment.body)
    ]


def get_answered_summary_comments(threads: list[ReviewThreadSchema]) -> set[tuple[str, str]]:
    answered = set()
    for thread in threads:
        for comment in thread.comments:
            reference = get_summary_reply_reference(comment.body)
            if reference is not None:
                answered.add(reference)
    return answered
