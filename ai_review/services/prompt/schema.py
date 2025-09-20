from pydantic import BaseModel, Field

from ai_review.config import settings


class PromptContextSchema(BaseModel):
    merge_request_title: str | None = None
    merge_request_description: str | None = None

    merge_request_author_name: str | None = None
    merge_request_author_username: str | None = None

    merge_request_reviewer: str | None = None
    merge_request_reviewers: list[str] = Field(default_factory=list)
    merge_request_reviewers_usernames: list[str] = Field(default_factory=list)

    merge_request_assignees: list[str] = Field(default_factory=list)
    merge_request_assignees_usernames: list[str] = Field(default_factory=list)

    source_branch: str | None = None
    target_branch: str | None = None

    labels: list[str] = Field(default_factory=list)
    changed_files: list[str] = Field(default_factory=list)

    @property
    def reviewers_format(self) -> str:
        return ", ".join(self.merge_request_reviewers)

    @property
    def reviewers_usernames_format(self) -> str:
        return ", ".join(self.merge_request_reviewers_usernames)

    @property
    def assignees_format(self) -> str:
        return ", ".join(self.merge_request_assignees)

    @property
    def assignees_usernames_format(self) -> str:
        return ", ".join(self.merge_request_assignees_usernames)

    @property
    def labels_format(self) -> str:
        return ", ".join(self.labels)

    @property
    def changed_files_format(self) -> str:
        return ", ".join(self.changed_files)

    def apply_format(self, prompt: str) -> str:
        return prompt.format(
            merge_request_title=self.merge_request_title or "",
            merge_request_description=self.merge_request_description or "",

            merge_request_author_name=self.merge_request_author_name or "",
            merge_request_author_username=self.merge_request_author_username or "",

            merge_request_reviewer=self.merge_request_reviewer or "",
            merge_request_reviewers=self.reviewers_format,
            merge_request_reviewers_usernames=self.reviewers_usernames_format,

            merge_request_assignees=self.assignees_format,
            merge_request_assignees_usernames=self.assignees_usernames_format,

            source_branch=self.source_branch or "",
            target_branch=self.target_branch or "",

            labels=self.labels_format,
            changed_files=self.changed_files_format,
            **settings.prompt.context
        )
