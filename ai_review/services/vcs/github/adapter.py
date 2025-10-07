from ai_review.clients.github.pr.schema.comments import GitHubPRCommentSchema, GitHubIssueCommentSchema
from ai_review.services.vcs.types import ReviewCommentSchema, UserSchema


def get_review_comment_from_github_pr_comment(comment: GitHubPRCommentSchema) -> ReviewCommentSchema:
    parent_id = comment.in_reply_to_id
    thread_id = parent_id or comment.id

    user = comment.user
    author = UserSchema(
        id=user.id if user else None,
        name=user.login if user else "",
        username=user.login if user else "",
    )

    return ReviewCommentSchema(
        id=comment.id,
        body=comment.body or "",
        file=comment.path,
        line=comment.line,
        author=author,
        parent_id=parent_id,
        thread_id=thread_id,
    )


def get_review_comment_from_github_issue_comment(comment: GitHubIssueCommentSchema) -> ReviewCommentSchema:
    return ReviewCommentSchema(id=comment.id, body=comment.body or "", thread_id=comment.id)
