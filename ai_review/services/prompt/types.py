from typing import Protocol

from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.vcs.types import ReviewThreadSchema


class PromptServiceProtocol(Protocol):
    def prepare_prompt(self, prompts: list[str], context: PromptContextSchema) -> str:
        ...

    def build_inline_request(self, diff: DiffFileSchema, context: PromptContextSchema) -> str:
        ...

    def build_summary_request(self, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        ...

    def build_context_request(self, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        ...

    def build_inline_reply_request(
            self,
            diff: DiffFileSchema,
            thread: ReviewThreadSchema,
            context: PromptContextSchema
    ) -> str:
        ...

    def build_summary_reply_request(
            self,
            diffs: list[DiffFileSchema],
            thread: ReviewThreadSchema,
            context: PromptContextSchema
    ) -> str:
        ...

    def build_system_inline_request(self, context: PromptContextSchema) -> str:
        ...

    def build_system_context_request(self, context: PromptContextSchema) -> str:
        ...

    def build_system_summary_request(self, context: PromptContextSchema) -> str:
        ...

    def build_system_inline_reply_request(self, context: PromptContextSchema) -> str:
        ...

    def build_system_summary_reply_request(self, context: PromptContextSchema) -> str:
        ...
