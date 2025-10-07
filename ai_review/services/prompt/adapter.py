from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.vcs.types import ReviewInfoSchema


def build_prompt_context_from_review_info(review: ReviewInfoSchema) -> PromptContextSchema:
    return PromptContextSchema(
        review_title=review.title,
        review_description=review.description,

        review_author_name=review.author.name,
        review_author_username=review.author.username,

        review_reviewers=[user.name for user in review.reviewers],
        review_reviewers_usernames=[user.username for user in review.reviewers],
        review_reviewer=review.reviewers[0].name if review.reviewers else "",

        review_assignees=[user.name for user in review.assignees],
        review_assignees_usernames=[user.username for user in review.assignees],

        source_branch=review.source_branch.ref,
        target_branch=review.target_branch.ref,

        labels=review.labels,
        changed_files=review.changed_files,
    )
