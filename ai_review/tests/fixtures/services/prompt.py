import pytest

from ai_review.libs.config.prompt import PromptConfig
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.prompt.schema import PromptContextSchema
from ai_review.services.prompt.types import PromptServiceProtocol
from ai_review.services.vcs.types import ReviewThreadSchema


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

    def build_inline_reply_request(
            self,
            diff: DiffFileSchema,
            thread: ReviewThreadSchema,
            context: PromptContextSchema
    ) -> str:
        self.calls.append(("build_inline_reply_request", {"diff": diff, "thread": thread, "context": context}))
        return f"INLINE_REPLY_PROMPT_FOR_{diff.file}"

    def build_summary_reply_request(
            self,
            diffs: list[DiffFileSchema],
            thread: ReviewThreadSchema,
            context: PromptContextSchema
    ) -> str:
        self.calls.append(("build_summary_reply_request", {"diffs": diffs, "thread": thread, "context": context}))
        return "SUMMARY_REPLY_PROMPT"

    def build_system_inline_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_inline_request", {"context": context}))
        return "SYSTEM_INLINE_PROMPT"

    def build_system_context_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_context_request", {"context": context}))
        return "SYSTEM_CONTEXT_PROMPT"

    def build_system_summary_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_summary_request", {"context": context}))
        return "SYSTEM_SUMMARY_PROMPT"

    def build_system_inline_reply_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_inline_reply_request", {"context": context}))
        return "SYSTEM_INLINE_REPLY_PROMPT"

    def build_system_summary_reply_request(self, context: PromptContextSchema) -> str:
        self.calls.append(("build_system_summary_reply_request", {"context": context}))
        return "SYSTEM_SUMMARY_REPLY_PROMPT"


@pytest.fixture
def fake_prompt_service() -> FakePromptService:
    return FakePromptService()


@pytest.fixture
def fake_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch methods of settings.prompt to return dummy values."""
    monkeypatch.setattr(PromptConfig, "load_inline", lambda self: ["GLOBAL_INLINE", "INLINE_PROMPT"])
    monkeypatch.setattr(PromptConfig, "load_context", lambda self: ["GLOBAL_CONTEXT", "CONTEXT_PROMPT"])
    monkeypatch.setattr(PromptConfig, "load_summary", lambda self: ["GLOBAL_SUMMARY", "SUMMARY_PROMPT"])
    monkeypatch.setattr(PromptConfig, "load_system_inline", lambda self: ["SYS_INLINE_A", "SYS_INLINE_B"])
    monkeypatch.setattr(PromptConfig, "load_system_context", lambda self: ["SYS_CONTEXT_A", "SYS_CONTEXT_B"])
    monkeypatch.setattr(PromptConfig, "load_system_summary", lambda self: ["SYS_SUMMARY_A", "SYS_SUMMARY_B"])
    monkeypatch.setattr(PromptConfig, "load_inline_reply", lambda self: ["INLINE_REPLY_A", "INLINE_REPLY_B"])
    monkeypatch.setattr(PromptConfig, "load_summary_reply", lambda self: ["SUMMARY_REPLY_A", "SUMMARY_REPLY_B"])
    monkeypatch.setattr(
        PromptConfig,
        "load_system_inline_reply",
        lambda self: ["SYS_INLINE_REPLY_A", "SYS_INLINE_REPLY_B"]
    )
    monkeypatch.setattr(
        PromptConfig,
        "load_system_summary_reply",
        lambda self: ["SYS_SUMMARY_REPLY_A", "SYS_SUMMARY_REPLY_B"]
    )


@pytest.fixture
def fake_prompt_context() -> PromptContextSchema:
    """Builds a context object that reflects the new unified review schema."""
    return PromptContextSchema(
        review_title="Fix login bug",
        review_description="Some description",
        review_author_name="Nikita",
        review_author_username="nikita.filonov",
        review_reviewers=["Alice", "Bob"],
        review_reviewers_usernames=["alice", "bob"],
        review_assignees=["Charlie"],
        review_assignees_usernames=["charlie"],
        source_branch="feature/login-fix",
        target_branch="main",
        labels=["bug", "critical"],
        changed_files=["foo.py", "bar.py"],
    )
