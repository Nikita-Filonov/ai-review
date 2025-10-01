from ai_review.config import settings
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.prompt.tools import normalize_prompt, format_file
from ai_review.services.prompt.types import PromptServiceProtocol


class PromptService(PromptServiceProtocol):
    @classmethod
    def prepare_prompt(cls, prompts: list[str], context: PromptContextSchema) -> str:
        prompt = "\n\n".join(prompts)
        prompt = context.apply_format(prompt)

        if settings.prompt.normalize_prompts:
            prompt = normalize_prompt(prompt)

        return prompt

    @classmethod
    def build_inline_request(cls, diff: DiffFileSchema, context: PromptContextSchema) -> str:
        prompt = cls.prepare_prompt(settings.prompt.load_inline(), context)
        return (
            f"{prompt}\n\n"
            f"## Diff\n\n"
            f"{format_file(diff)}"
        )

    @classmethod
    def build_summary_request(cls, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        prompt = cls.prepare_prompt(settings.prompt.load_summary(), context)
        changes = "\n\n".join(map(format_file, diffs))
        return (
            f"{prompt}\n\n"
            f"## Changes\n\n"
            f"{changes}\n"
        )

    @classmethod
    def build_context_request(cls, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        prompt = cls.prepare_prompt(settings.prompt.load_context(), context)
        changes = "\n\n".join(map(format_file, diffs))
        return (
            f"{prompt}\n\n"
            f"## Diff\n\n"
            f"{changes}\n"
        )

    @classmethod
    def build_system_inline_request(cls, context: PromptContextSchema) -> str:
        return cls.prepare_prompt(settings.prompt.load_system_inline(), context)

    @classmethod
    def build_system_context_request(cls, context: PromptContextSchema) -> str:
        return cls.prepare_prompt(settings.prompt.load_system_context(), context)

    @classmethod
    def build_system_summary_request(cls, context: PromptContextSchema) -> str:
        return cls.prepare_prompt(settings.prompt.load_system_summary(), context)
