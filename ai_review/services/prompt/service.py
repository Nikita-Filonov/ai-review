from ai_review.config import settings
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema


def format_file(diff: DiffFileSchema) -> str:
    return f"# File: {diff.file}\n{diff.diff}\n"


class PromptService:
    @classmethod
    def build_inline_request(cls, diff: DiffFileSchema, context: PromptContextSchema) -> str:
        inline_prompts = "\n\n".join(settings.prompt.load_inline())
        prompt = (
            f"{inline_prompts}\n\n"
            f"## Diff\n\n"
            f"{format_file(diff)}"
        )
        return context.apply_format(prompt)

    @classmethod
    def build_summary_request(cls, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        changes = "\n\n".join(map(format_file, diffs))
        summary_prompts = "\n\n".join(settings.prompt.load_summary())
        prompt = (
            f"{summary_prompts}\n\n"
            f"## Changes\n\n"
            f"{changes}\n"
        )
        return context.apply_format(prompt)

    @classmethod
    def build_context_request(cls, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        changes = "\n\n".join(map(format_file, diffs))
        inline_prompts = "\n\n".join(settings.prompt.load_context())
        prompt = (
            f"{inline_prompts}\n\n"
            f"## Diff\n\n"
            f"{changes}\n"
        )
        return context.apply_format(prompt)

    @classmethod
    def build_system_inline_request(cls, context: PromptContextSchema) -> str:
        prompt = "\n\n".join(settings.prompt.load_system_inline())
        return context.apply_format(prompt)

    @classmethod
    def build_system_context_request(cls, context: PromptContextSchema) -> str:
        prompt = "\n\n".join(settings.prompt.load_system_context())
        return context.apply_format(prompt)

    @classmethod
    def build_system_summary_request(cls, context: PromptContextSchema) -> str:
        prompt = "\n\n".join(settings.prompt.load_system_summary())
        return context.apply_format(prompt)
