from ai_review.clients.bitbucket_server.pr.schema.activities import (
    BitbucketServerActivitySchema,
)
from ai_review.clients.bitbucket_server.pr.schema.comments import BitbucketServerCommentSchema


def get_comments_from_activities(
        activities: list[BitbucketServerActivitySchema],
) -> list[BitbucketServerCommentSchema]:
    return [
        activity.comment
        for activity in activities
        if activity.action == "COMMENTED" and activity.comment is not None
    ]
