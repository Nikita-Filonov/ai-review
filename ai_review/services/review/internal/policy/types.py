from typing import Protocol


class ReviewPolicyServiceProtocol(Protocol):
    def should_review_file(self, file: str) -> bool:
        ...

    def apply_for_files(self, files: list[str]) -> list[str]:
        ...

    def apply_for_inline_comments(self, comments: list) -> list:
        ...

    def apply_for_context_comments(self, comments: list) -> list:
        ...
