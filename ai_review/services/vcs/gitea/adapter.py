from ai_review.clients.gitea.pr.schema.comments import GiteaPRCommentSchema
from ai_review.clients.gitea.pr.schema.pull_request import GiteaUserSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_user_from_gitea_user(user: GiteaUserSchema | None) -> UserSchema:
    return UserSchema(
        id=user.id if user else None,
        name=user.login if user else "",
        username=user.login if user else "",
    )


def get_review_comment_from_gitea_comment(comment: GiteaPRCommentSchema) -> ReviewCommentSchema:
    return ReviewCommentSchema(
        id=comment.id,
        body=comment.body or "",
        file=comment.path,
        line=comment.line,
        author=get_user_from_gitea_user(comment.user),
        thread_id=comment.id
    )
