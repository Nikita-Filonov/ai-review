from collections.abc import Awaitable, Iterable

from ai_review.config import settings
from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.artifacts.types import ArtifactsServiceProtocol
from ai_review.services.hook import hook
from ai_review.services.review.filter.types import ReviewFilterServiceProtocol
from ai_review.services.review.gateway.types import ReviewCommentGatewayProtocol
from ai_review.services.review.internal.inline.schema import InlineCommentListSchema, InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ReviewThreadSchema,
    ReviewCommentSchema,
    SupportsBatchedComments,
)

logger = get_logger("REVIEW_COMMENT_GATEWAY")


class ReviewCommentGateway(ReviewCommentGatewayProtocol):
    def __init__(
            self,
            vcs: VCSClientProtocol,
            artifacts: ArtifactsServiceProtocol,
            review_filter: ReviewFilterServiceProtocol,
    ):
        self.vcs = vcs
        self.artifacts = artifacts
        self.review_filter = review_filter

    @staticmethod
    async def delete_comments(deletions: Iterable[Awaitable[None]]) -> None:
        for result in await bounded_gather(deletions):
            if isinstance(result, BaseException):
                raise result

    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        threads = await self.vcs.get_inline_threads()
        inline_threads = self.review_filter.filter_inline_threads(threads)
        logger.info(f"Detected {len(inline_threads)}/{len(threads)} AI inline threads")
        return inline_threads

    async def get_summary_threads(self) -> list[ReviewThreadSchema]:
        threads = await self.vcs.get_general_threads()
        summary_threads = self.review_filter.filter_summary_threads(threads)
        logger.info(f"Detected {len(summary_threads)}/{len(threads)} AI summary threads")
        return summary_threads

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        comments = await self.vcs.get_inline_comments()
        inline_comments = self.review_filter.filter_inline_comments(comments)
        logger.info(f"Detected {len(inline_comments)}/{len(comments)} AI inline comments")
        return inline_comments

    async def get_summary_comments(self) -> list[ReviewCommentSchema]:
        comments = await self.vcs.get_general_comments()
        summary_comments = self.review_filter.filter_summary_comments(comments)
        logger.info(f"Detected {len(summary_comments)}/{len(comments)} AI summary comments")
        return summary_comments

    async def get_clearable_summary_comments(self) -> list[ReviewCommentSchema]:
        comments = await self.vcs.get_general_comments()
        clearable_comments = self.review_filter.filter_clearable_summary_comments(comments)
        logger.info(f"Detected {len(clearable_comments)}/{len(comments)} clearable AI general comments")
        return clearable_comments

    async def get_inline_replies(self) -> list[ReviewCommentSchema]:
        comments = await self.vcs.get_inline_comments()
        replies = self.review_filter.filter_inline_replies(comments)
        logger.info(f"Detected {len(replies)}/{len(comments)} inline replies")
        return replies

    async def get_general_inline_replies(self) -> list[ReviewCommentSchema]:
        comments = await self.vcs.get_general_comments()
        replies = self.review_filter.filter_inline_replies(comments)
        logger.info(f"Detected {len(replies)}/{len(comments)} general inline replies")
        return replies

    async def get_generated_general_inline_replies(self) -> list[ReviewCommentSchema]:
        """Some VCS adapters post generated inline replies as general comments."""
        comments = await self.vcs.get_general_comments()
        replies = self.review_filter.filter_generated_inline_replies(comments)
        logger.info(f"Detected {len(replies)}/{len(comments)} general AI inline replies")
        return replies

    async def get_summary_replies(self) -> list[ReviewCommentSchema]:
        comments = await self.vcs.get_general_comments()
        replies = self.review_filter.filter_summary_replies(comments)
        logger.info(f"Detected {len(replies)}/{len(comments)} summary replies")
        return replies

    async def process_inline_reply(self, thread_id: str, reply: InlineCommentReplySchema) -> None:
        try:
            await hook.emit_inline_comment_reply_start(reply)
            await self.vcs.create_inline_reply(thread_id, reply.body_with_tag)
            await hook.emit_inline_comment_reply_complete(reply)

            await self.artifacts.save_vcs_inline_reply(thread_id, reply)
        except Exception as error:
            logger.exception(f"Failed to create inline reply for thread {thread_id}: {error}")
            await hook.emit_inline_comment_reply_error(reply)

    async def process_summary_reply(
            self,
            thread_id: str | int,
            reply: SummaryCommentReplySchema,
            *,
            request_comment_id: str | int,
    ) -> None:
        try:
            await hook.emit_summary_comment_reply_start(reply)
            await self.vcs.create_summary_reply(thread_id, reply.body_for_request(thread_id, request_comment_id))
            await hook.emit_summary_comment_reply_complete(reply)

            await self.artifacts.save_vcs_summary_reply(thread_id, reply)
        except Exception as error:
            logger.exception(f"Failed to create summary reply for thread {thread_id}: {error}")
            await hook.emit_summary_comment_reply_error(reply)

    async def process_inline_comment(self, comment: InlineCommentSchema) -> None:
        try:
            await hook.emit_inline_comment_start(comment)
            await self.vcs.create_inline_comment(
                file=comment.file,
                line=comment.line,
                message=comment.body_with_tag,
            )
            await hook.emit_inline_comment_complete(comment)

            await self.artifacts.save_vcs_inline(comment)
        except Exception as error:
            logger.exception(
                f"Failed to process inline comment for {comment.file}:{comment.line} — {error}"
            )
            await hook.emit_inline_comment_error(comment)

            if settings.review.inline_comment_fallback:
                logger.warning(f"Falling back to general comment for {comment.file}:{comment.line}")
                await self.process_inline_fallback_comment(SummaryCommentSchema(text=comment.fallback_body))

    async def process_inline_fallback_comment(self, comment: SummaryCommentSchema) -> None:
        try:
            await hook.emit_summary_comment_start(comment)
            await self.vcs.create_general_comment(comment.body_with_fallback_tag)
            await hook.emit_summary_comment_complete(comment)

            await self.artifacts.save_vcs_summary(comment)
        except Exception as error:
            logger.exception(f"Failed to process inline fallback comment: {comment} — {error}")
            await hook.emit_summary_comment_error(comment)

    async def process_summary_comment(self, comment: SummaryCommentSchema) -> None:
        try:
            await hook.emit_summary_comment_start(comment)
            await self.vcs.create_general_comment(comment.body_with_tag)
            await hook.emit_summary_comment_complete(comment)

            await self.artifacts.save_vcs_summary(comment)
        except Exception as error:
            logger.exception(f"Failed to process summary comment: {comment} — {error}")
            await hook.emit_summary_comment_error(comment)

    async def process_inline_comments(self, comments: InlineCommentListSchema) -> None:
        await bounded_gather([self.process_inline_comment(comment) for comment in comments.root])

    async def finalize(self) -> None:
        if not isinstance(self.vcs, SupportsBatchedComments):
            return

        try:
            await self.vcs.publish_comments()
        except Exception as error:
            logger.exception(f"Failed to publish batched comments: {error}")

    async def clear_inline_comments(self) -> None:
        await hook.emit_clear_inline_comments_start()

        try:
            comments = await self.get_inline_comments()
            general_replies = await self.get_generated_general_inline_replies()
            general_replies = self.review_filter.exclude_duplicate_comments(general_replies, comments)
            if not comments and not general_replies:
                logger.info("No AI inline comments to clear")
                await hook.emit_clear_inline_comments_complete(comments=[])
                return

            logger.info(f"Clearing {len(comments) + len(general_replies)} AI inline comments")

            replies, findings = self.review_filter.partition_inline_comments(comments)
            await self.delete_comments(self.vcs.delete_inline_comment(reply.id) for reply in replies)
            await self.delete_comments(self.vcs.delete_general_comment(reply.id) for reply in general_replies)
            await self.delete_comments(self.vcs.delete_inline_comment(comment.id) for comment in findings)
            await hook.emit_clear_inline_comments_complete(comments=[*comments, *general_replies])
        except Exception as error:
            logger.exception(f"Failed to clear inline comments: {error}")
            await hook.emit_clear_inline_comments_error()
            raise

    async def clear_summary_comments(self) -> None:
        await hook.emit_clear_summary_comments_start()

        try:
            comments = await self.get_clearable_summary_comments()
            if not comments:
                logger.info("No AI summary comments to clear")
                await hook.emit_clear_summary_comments_complete(comments=comments)
                return

            logger.info(f"Clearing {len(comments)} AI summary comments")

            replies, findings = self.review_filter.partition_summary_comments(comments)
            await self.delete_comments(self.vcs.delete_general_comment(reply.id) for reply in replies)
            await self.delete_comments(self.vcs.delete_general_comment(comment.id) for comment in findings)
            await hook.emit_clear_summary_comments_complete(comments=comments)
        except Exception as error:
            logger.exception(f"Failed to clear summary comments: {error}")
            await hook.emit_clear_summary_comments_error()
            raise

    async def clear_inline_replies(self) -> None:
        try:
            replies = await self.get_inline_replies()
            general_replies = await self.get_general_inline_replies()
            general_replies = self.review_filter.exclude_duplicate_comments(general_replies, replies)
            logger.info(f"Clearing {len(replies) + len(general_replies)} inline replies")
            await self.delete_comments(self.vcs.delete_inline_comment(reply.id) for reply in replies)
            await self.delete_comments(self.vcs.delete_general_comment(reply.id) for reply in general_replies)
        except Exception as error:
            logger.exception(f"Failed to clear inline replies: {error}")
            raise

    async def clear_summary_replies(self) -> None:
        try:
            replies = await self.get_summary_replies()
            logger.info(f"Clearing {len(replies)} summary replies")
            await self.delete_comments(self.vcs.delete_general_comment(reply.id) for reply in replies)
        except Exception as error:
            logger.exception(f"Failed to clear summary replies: {error}")
            raise
