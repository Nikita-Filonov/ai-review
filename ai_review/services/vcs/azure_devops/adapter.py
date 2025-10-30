from ai_review.clients.azure_devops.pr.schema.threads import AzureDevOpsCommentSchema, AzureDevOpsThreadSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_review_comment_from_azure_devops_comment(
    comment: AzureDevOpsCommentSchema,
    thread: AzureDevOpsThreadSchema
) -> ReviewCommentSchema:
    """Convert Azure DevOps comment to ReviewCommentSchema"""
    file_path = None
    line = None
    
    if thread.thread_context:
        file_path = thread.thread_context.file_path
        if thread.thread_context.right_file_end:
            line = thread.thread_context.right_file_end.get("line")
    
    return ReviewCommentSchema(
        id=comment.id,
        body=comment.content,
        file=file_path,
        line=line,
        author=UserSchema(
            id=comment.author.id,
            name=comment.author.display_name,
            username=comment.author.unique_name
        ),
        parent_id=comment.parent_comment_id if comment.parent_comment_id > 0 else None,
        thread_id=thread.id
    )

