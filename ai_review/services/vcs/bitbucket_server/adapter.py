from ai_review.clients.bitbucket_server.pr.schema.comments import BitbucketServerCommentSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_review_comment_from_bitbucket_server_comment(comment: BitbucketServerCommentSchema) -> ReviewCommentSchema:
    parent_id = None
    thread_id = comment.id

    user = comment.author
    author = UserSchema(
        id=user.id if user else None,
        name=user.display_name or user.name or "",
        username=user.slug or user.name or "",
    )

    file = comment.anchor.path if comment.anchor and comment.anchor.path else None
    line = comment.anchor.line if comment.anchor else None

    return ReviewCommentSchema(
        id=comment.id,
        body=comment.text or "",
        file=file,
        line=line,
        author=author,
        parent_id=parent_id,
        thread_id=thread_id,
    )
