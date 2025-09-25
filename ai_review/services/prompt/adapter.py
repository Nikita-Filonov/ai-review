from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.vcs.types import MRInfoSchema


def build_prompt_context_from_mr_info(mr: MRInfoSchema) -> PromptContextSchema:
    return PromptContextSchema(
        merge_request_title=mr.title,
        merge_request_description=mr.description,

        merge_request_author_name=mr.author.name,
        merge_request_author_username=mr.author.username,

        merge_request_reviewers=[reviewer.name for reviewer in mr.reviewers],
        merge_request_reviewers_usernames=[reviewer.username for reviewer in mr.reviewers],
        merge_request_reviewer=mr.reviewers[0].name if mr.reviewers else "",

        merge_request_assignees=[assignee.name for assignee in mr.assignees],
        merge_request_assignees_usernames=[assignee.username for assignee in mr.assignees],

        source_branch=mr.source_branch,
        target_branch=mr.target_branch,

        labels=mr.labels,
        changed_files=mr.changed_files,
    )
