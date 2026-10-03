from ai_review.config import settings
from ai_review.libs.text import contains_tag
from ai_review.services.review.filter.tools import filter_replies, get_answered_summary_comments
from ai_review.services.review.filter.types import ReviewFilterServiceProtocol
from ai_review.services.review.internal.inline_reply.tools import is_inline_reply
from ai_review.services.review.internal.summary_reply.tools import get_summary_reply_reference
from ai_review.services.vcs.types import ReviewCommentSchema, ReviewThreadSchema


class ReviewFilterService(ReviewFilterServiceProtocol):
    """Select review comments and threads using configured tags and generated markers."""

    def __init__(self):
        self.review = settings.review

    def filter_inline_threads(self, threads: list[ReviewThreadSchema]) -> list[ReviewThreadSchema]:
        selected = []
        for thread in threads:
            latest = thread.latest_comment
            if latest is None:
                continue
            if not contains_tag(latest.body, self.review.inline_reply_tag):
                continue
            if contains_tag(latest.body, self.review.inline_tag):
                continue
            selected.append(thread)
        return selected

    def filter_summary_threads(self, threads: list[ReviewThreadSchema]) -> list[ReviewThreadSchema]:
        answered = get_answered_summary_comments(threads)
        selected = []
        for thread in threads:
            latest = thread.latest_comment
            if latest is None:
                continue
            if not contains_tag(latest.body, self.review.summary_reply_tag):
                continue
            if contains_tag(latest.body, self.review.summary_tag):
                continue
            if get_summary_reply_reference(latest.body) is not None:
                continue
            if (str(thread.id), str(latest.id)) in answered:
                continue
            selected.append(thread)
        return selected

    def filter_inline_comments(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        return [
            comment for comment in comments
            if contains_tag(comment.body, self.review.inline_tag) or is_inline_reply(comment.body)
        ]

    def filter_summary_comments(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        """Only original summaries suppress a new summary review."""
        return [
            comment for comment in comments
            if contains_tag(comment.body, self.review.summary_tag)
               and get_summary_reply_reference(comment.body) is None
        ]

    def filter_clearable_summary_comments(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        """Summary cleanup also includes generated replies and inline fallbacks."""
        return [
            comment for comment in comments
            if contains_tag(comment.body, self.review.summary_tag)
               or contains_tag(comment.body, self.review.inline_fallback_tag)
               or get_summary_reply_reference(comment.body) is not None
        ]

    def filter_inline_replies(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        return filter_replies(comments, self.review.inline_reply_tag)

    def filter_summary_replies(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        return filter_replies(comments, self.review.summary_reply_tag)

    def filter_generated_inline_replies(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        return [comment for comment in comments if is_inline_reply(comment.body)]

    def partition_inline_comments(
            self, comments: list[ReviewCommentSchema],
    ) -> tuple[list[ReviewCommentSchema], list[ReviewCommentSchema]]:
        """Separate generated replies from findings for deletion in that order."""
        replies = []
        findings = []
        for comment in comments:
            if is_inline_reply(comment.body):
                replies.append(comment)
            else:
                findings.append(comment)
        return replies, findings

    def partition_summary_comments(
            self, comments: list[ReviewCommentSchema],
    ) -> tuple[list[ReviewCommentSchema], list[ReviewCommentSchema]]:
        """Separate generated replies from summaries and inline fallbacks."""
        replies = []
        findings = []
        for comment in comments:
            if get_summary_reply_reference(comment.body) is not None:
                replies.append(comment)
            else:
                findings.append(comment)
        return replies, findings
