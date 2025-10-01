from typing import Protocol

from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema


class PromptServiceProtocol(Protocol):
    def prepare_prompt(self, prompts: list[str], context: PromptContextSchema) -> str:
        ...

    def build_inline_request(self, diff: DiffFileSchema, context: PromptContextSchema) -> str:
        ...

    def build_summary_request(self, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        ...

    def build_context_request(self, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        ...

    def build_system_inline_request(self, context: PromptContextSchema) -> str:
        ...

    def build_system_context_request(self, context: PromptContextSchema) -> str:
        ...

    def build_system_summary_request(self, context: PromptContextSchema) -> str:
        ...
