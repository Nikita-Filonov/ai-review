from pydantic import BaseModel, Field

from ai_review.config import settings
from ai_review.libs.template.render import render_template


class PromptContextSchema(BaseModel):
    merge_request_title: str = ""
    merge_request_description: str = ""

    merge_request_author_name: str = ""
    merge_request_author_username: str = ""

    merge_request_reviewer: str = ""
    merge_request_reviewers: list[str] = Field(default_factory=list)
    merge_request_reviewers_usernames: list[str] = Field(default_factory=list)

    merge_request_assignees: list[str] = Field(default_factory=list)
    merge_request_assignees_usernames: list[str] = Field(default_factory=list)

    source_branch: str = ""
    target_branch: str = ""

    labels: list[str] = Field(default_factory=list)
    changed_files: list[str] = Field(default_factory=list)

    @property
    def render_values(self) -> dict[str, str]:
        return {
            "merge_request_title": self.merge_request_title,
            "merge_request_description": self.merge_request_description,

            "merge_request_author_name": self.merge_request_author_name,
            "merge_request_author_username": self.merge_request_author_username,

            "merge_request_reviewer": self.merge_request_reviewer,
            "merge_request_reviewers": ", ".join(self.merge_request_reviewers),
            "merge_request_reviewers_usernames": ", ".join(self.merge_request_reviewers_usernames),

            "merge_request_assignees": ", ".join(self.merge_request_assignees),
            "merge_request_assignees_usernames": ", ".join(self.merge_request_assignees_usernames),

            "source_branch": self.source_branch,
            "target_branch": self.target_branch,

            "labels": ", ".join(self.labels),
            "changed_files": ", ".join(self.changed_files),
        }

    def apply_format(self, prompt: str) -> str:
        values = {**self.render_values, **settings.prompt.context}
        return render_template(prompt, values, settings.prompt.context_placeholder)
