from ai_review.clients.bitbucket.pr.schema.comments import BitbucketPRCommentSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_review_comment_from_bitbucket_pr_comment(comment: BitbucketPRCommentSchema) -> ReviewCommentSchema:
    parent_id = comment.parent.id if comment.parent else None
    thread_id = parent_id or comment.id

    user = comment.user
    author = UserSchema(
        id=user.uuid if user else None,
        name=user.display_name if user else "",
        username=user.nickname if user else "",
    )

    return ReviewCommentSchema(
        id=comment.id,
        body=comment.content.raw or "",
        file=comment.inline.path if comment.inline else None,
        line=comment.inline.to_line if comment.inline else None,
        author=author,
        parent_id=parent_id,
        thread_id=thread_id,
    )
