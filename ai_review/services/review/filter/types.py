from typing import Protocol

from ai_review.services.vcs.types import ReviewCommentSchema, ReviewThreadSchema


class ReviewFilterServiceProtocol(Protocol):
    def exclude_duplicate_comments(
            self,
            comments: list[ReviewCommentSchema],
            selected: list[ReviewCommentSchema],
    ) -> list[ReviewCommentSchema]:
        ...

    def filter_inline_threads(self, threads: list[ReviewThreadSchema]) -> list[ReviewThreadSchema]:
        ...

    def filter_summary_threads(self, threads: list[ReviewThreadSchema]) -> list[ReviewThreadSchema]:
        ...

    def filter_inline_comments(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        ...

    def filter_summary_comments(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        ...

    def filter_clearable_summary_comments(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        ...

    def filter_inline_replies(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        ...

    def filter_summary_replies(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        ...

    def filter_generated_inline_replies(self, comments: list[ReviewCommentSchema]) -> list[ReviewCommentSchema]:
        ...

    def partition_inline_comments(
            self, comments: list[ReviewCommentSchema],
    ) -> tuple[list[ReviewCommentSchema], list[ReviewCommentSchema]]:
        ...

    def partition_summary_comments(
            self, comments: list[ReviewCommentSchema],
    ) -> tuple[list[ReviewCommentSchema], list[ReviewCommentSchema]]:
        ...
