from ai_review.clients.gitlab.mr.schema.discussions import GitLabDiscussionSchema
from ai_review.clients.gitlab.mr.schema.notes import GitLabNoteSchema
from ai_review.clients.gitlab.mr.schema.user import GitLabUserSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_user_from_gitlab_user(user: GitLabUserSchema | None) -> UserSchema:
    return UserSchema(
        id=user.id if user else None,
        name=user.name if user else "",
        username=user.username if user else "",
    )


def get_review_comment_from_gitlab_note(
        note: GitLabNoteSchema,
        discussion: GitLabDiscussionSchema
) -> ReviewCommentSchema:
    position = note.position or discussion.position

    return ReviewCommentSchema(
        id=note.id,
        body=note.body or "",
        file=position.new_path if position else None,
        line=position.new_line if position else None,
        author=get_user_from_gitlab_user(note.author),
        thread_id=discussion.id,
    )
