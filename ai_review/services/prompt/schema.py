from pydantic import BaseModel, Field, field_serializer

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

    @field_serializer(
        "review_reviewers",
        "review_reviewers_usernames",
        "review_assignees",
        "review_assignees_usernames",
        "labels",
        "changed_files",
        when_used="always"
    )
    def list_of_strings_serializer(self, value: list[str]) -> str:
        return ", ".join(value)

    def apply_format(self, prompt: str) -> str:
        values = {**self.model_dump(), **settings.prompt.context}
        return render_template(prompt, values, settings.prompt.context_placeholder)
