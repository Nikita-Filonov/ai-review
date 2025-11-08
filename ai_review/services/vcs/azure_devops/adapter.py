from ai_review.clients.azure_devops.pr.schema.threads import (
    AzureDevOpsPRThreadSchema,
    AzureDevOpsPRCommentSchema,
)
from ai_review.clients.azure_devops.pr.schema.user import AzureDevOpsUserSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_user_from_azure_devops_user(user: AzureDevOpsUserSchema | None) -> UserSchema:
    return UserSchema(
        id=user.id if user else None,
        name=(user.display_name or "") if user else "",
        username=(user.unique_name or "") if user else "",
    )


def get_review_comment_from_azure_devops_comment(
        comment: AzureDevOpsPRCommentSchema,
        thread: AzureDevOpsPRThreadSchema,
) -> ReviewCommentSchema:
    context = thread.thread_context
    return ReviewCommentSchema(
        id=comment.id,
        body=comment.content or "",
        file=context.file_path if context else None,
        line=context.right_file_start.line if context and context.right_file_start else None,
        author=get_user_from_azure_devops_user(comment.author),
        thread_id=thread.id,
    )
