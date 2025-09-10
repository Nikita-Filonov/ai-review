from clients.gitlab.mr.schema.comments import GitLabCreateMRCommentRequestSchema
from services.review.summary.schema import SummaryCommentSchema


def build_gitlab_create_mr_comment_request(
        summary: SummaryCommentSchema
) -> GitLabCreateMRCommentRequestSchema:
    return GitLabCreateMRCommentRequestSchema(body=summary.text)
