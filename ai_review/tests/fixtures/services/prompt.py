import pytest

from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.prompt.types import PromptServiceProtocol


class FakePromptService(PromptServiceProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def prepare_prompt(self, prompts: list[str], context: PromptContextSchema) -> str:
        self.calls.append(("prepare_prompt", {"prompts": prompts, "context": context}))
        return "FAKE_PROMPT"

    def build_inline_request(self, diff: DiffFileSchema, context: PromptContextSchema) -> str:
        self.calls.append(("build_inline_request", {"diff": diff, "context": context}))
        return f"INLINE_PROMPT_FOR_{diff.file}"

    def build_summary_request(self, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        self.calls.append(("build_summary_request", {"diffs": diffs, "context": context}))
        return "SUMMARY_PROMPT"

    def build_context_request(self, diffs: list[DiffFileSchema], context: PromptContextSchema) -> str:
        self.calls.append(("build_context_request", {"diffs": diffs, "context": context}))
        return "CONTEXT_PROMPT"

    def build_system_inline_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_inline_request", {"context": context}))
        return "SYSTEM_INLINE_PROMPT"

    def build_system_context_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_context_request", {"context": context}))
        return "SYSTEM_CONTEXT_PROMPT"

    def build_system_summary_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_summary_request", {"context": context}))
        return "SYSTEM_SUMMARY_PROMPT"


@pytest.fixture
def fake_prompt_service() -> FakePromptService:
    return FakePromptService()
