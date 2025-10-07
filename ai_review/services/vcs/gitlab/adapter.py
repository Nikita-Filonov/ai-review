from ai_review.clients.gitlab.mr.schema.discussions import GitLabDiscussionSchema
from ai_review.clients.gitlab.mr.schema.notes import GitLabNoteSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_review_comment_from_gitlab_note(
        note: GitLabNoteSchema,
        discussion: GitLabDiscussionSchema
) -> ReviewCommentSchema:
    user = note.author
    author = UserSchema(
        id=user.id if user else None,
        name=user.name if user else "",
        username=user.username if user else "",
    )

    return ReviewCommentSchema(
        id=note.id,
        body=note.body or "",
        file=discussion.position.new_path if discussion.position else None,
        line=discussion.position.new_line if discussion.position else None,
        author=author,
        thread_id=discussion.id,
    )
