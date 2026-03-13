from typing import Protocol


class PolicyServiceProtocol(Protocol):
    def should_review_file(self, file: str) -> bool:
        ...

    def should_agent_run_command(self, command: str) -> bool:
        ...

    def apply_for_files(self, files: list[str]) -> list[str]:
        ...

    def apply_for_inline_comments(self, comments: list) -> list:
        ...

    def apply_for_context_comments(self, comments: list) -> list:
        ...
