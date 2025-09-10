from clients.gitlab.mr.schema.discussions import (
    GitLabCreateMRDiscussionRequestSchema,
    GitLabDiscussionPositionSchema,
)
from services.review.inline.schema import InlineCommentSchema, InlineCommentListSchema


def build_gitlab_create_mr_discussion_request(
        comment: InlineCommentSchema,
        base_sha: str,
        head_sha: str,
        start_sha: str,
) -> GitLabCreateMRDiscussionRequestSchema:
    return GitLabCreateMRDiscussionRequestSchema(
        body=comment.comment,
        position=GitLabDiscussionPositionSchema(
            position_type="text",
            base_sha=base_sha,
            head_sha=head_sha,
            start_sha=start_sha,
            new_path=comment.file,
            new_line=comment.line,
        ),
    )


def build_gitlab_create_mr_discussion_requests(
        comments: InlineCommentListSchema,
        base_sha: str,
        head_sha: str,
        start_sha: str,
) -> list[GitLabCreateMRDiscussionRequestSchema]:
    return [
        build_gitlab_create_mr_discussion_request(
            comment=comment,
            base_sha=base_sha,
            head_sha=head_sha,
            start_sha=start_sha
        )
        for comment in comments.root
    ]
