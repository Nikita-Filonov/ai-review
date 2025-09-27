from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, FilePath, Field

from ai_review.libs.resources import load_resource


class PromptConfig(BaseModel):
    context: dict[str, str] = Field(default_factory=dict)
    normalize_prompts: bool = True
    context_placeholder: str = "<<{value}>>"
    inline_prompt_files: list[FilePath] | None = None
    context_prompt_files: list[FilePath] | None = None
    summary_prompt_files: list[FilePath] | None = None
    system_inline_prompt_files: list[FilePath] | None = None
    system_context_prompt_files: list[FilePath] | None = None
    system_summary_prompt_files: list[FilePath] | None = None
    include_inline_system_prompts: bool = True
    include_context_system_prompts: bool = True
    include_summary_system_prompts: bool = True

    @cached_property
    def inline_prompt_files_or_default(self) -> list[Path]:
        return self.inline_prompt_files or [
            load_resource(
                package="ai_review.prompts",
                filename="default_inline.md",
                fallback="ai_review/prompts/default_inline.md"
            )
        ]

    @cached_property
    def context_prompt_files_or_default(self) -> list[Path]:
        return self.context_prompt_files or [
            load_resource(
                package="ai_review.prompts",
                filename="default_context.md",
                fallback="ai_review/prompts/default_context.md"
            )
        ]

    @cached_property
    def summary_prompt_files_or_default(self) -> list[Path]:
        return self.summary_prompt_files or [
            load_resource(
                package="ai_review.prompts",
                filename="default_summary.md",
                fallback="ai_review/prompts/default_summary.md"
            )
        ]

    @cached_property
    def system_inline_prompt_files_or_default(self) -> list[Path]:
        global_files = [
            load_resource(
                package="ai_review.prompts",
                filename="default_system_inline.md",
                fallback="ai_review/prompts/default_system_inline.md"
            )
        ]

        if self.system_inline_prompt_files is None:
            return global_files

        if self.include_inline_system_prompts:
            return global_files + self.system_inline_prompt_files

        return self.system_inline_prompt_files

    @cached_property
    def system_context_prompt_files_or_default(self) -> list[Path]:
        global_files = [
            load_resource(
                package="ai_review.prompts",
                filename="default_system_context.md",
                fallback="ai_review/prompts/default_system_context.md"
            )
        ]

        if self.system_context_prompt_files is None:
            return global_files

        if self.include_context_system_prompts:
            return global_files + self.system_context_prompt_files

        return self.system_context_prompt_files

    @cached_property
    def system_summary_prompt_files_or_default(self) -> list[Path]:
        global_files = [
            load_resource(
                package="ai_review.prompts",
                filename="default_system_summary.md",
                fallback="ai_review/prompts/default_system_summary.md"
            )
        ]

        if self.system_summary_prompt_files is None:
            return global_files

        if self.include_summary_system_prompts:
            return global_files + self.system_summary_prompt_files

        return self.system_summary_prompt_files

    def load_inline(self) -> list[str]:
        return [file.read_text(encoding="utf-8") for file in self.inline_prompt_files_or_default]

    def load_context(self) -> list[str]:
        return [file.read_text(encoding="utf-8") for file in self.context_prompt_files_or_default]

    def load_summary(self) -> list[str]:
        return [file.read_text(encoding="utf-8") for file in self.summary_prompt_files_or_default]

    def load_system_inline(self) -> list[str]:
        return [file.read_text(encoding="utf-8") for file in self.system_inline_prompt_files_or_default]

    def load_system_context(self) -> list[str]:
        return [file.read_text(encoding="utf-8") for file in self.system_context_prompt_files_or_default]

    def load_system_summary(self) -> list[str]:
        return [file.read_text(encoding="utf-8") for file in self.system_summary_prompt_files_or_default]
