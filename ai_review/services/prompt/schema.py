from pydantic import BaseModel, Field

from ai_review.config import settings
from ai_review.libs.template.render import render_template


class PromptContextSchema(BaseModel):
    review_title: str = ""
    review_description: str = ""

    review_author_name: str = ""
    review_author_username: str = ""

    review_reviewer: str = ""
    review_reviewers: list[str] = Field(default_factory=list)
    review_reviewers_usernames: list[str] = Field(default_factory=list)

    review_assignees: list[str] = Field(default_factory=list)
    review_assignees_usernames: list[str] = Field(default_factory=list)

    source_branch: str = ""
    target_branch: str = ""

    labels: list[str] = Field(default_factory=list)
    changed_files: list[str] = Field(default_factory=list)

    @property
    def render_values(self) -> dict[str, str]:
        return {
            "review_title": self.review_title,
            "review_description": self.review_description,

            "review_author_name": self.review_author_name,
            "review_author_username": self.review_author_username,

            "review_reviewer": self.review_reviewer,
            "review_reviewers": ", ".join(self.review_reviewers),
            "review_reviewers_usernames": ", ".join(self.review_reviewers_usernames),

            "review_assignees": ", ".join(self.review_assignees),
            "review_assignees_usernames": ", ".join(self.review_assignees_usernames),

            "source_branch": self.source_branch,
            "target_branch": self.target_branch,

            "labels": ", ".join(self.labels),
            "changed_files": ", ".join(self.changed_files),
        }

    def apply_format(self, prompt: str) -> str:
        values = {**self.render_values, **settings.prompt.context}
        return render_template(prompt, values, settings.prompt.context_placeholder)
