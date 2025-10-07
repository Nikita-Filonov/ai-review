from typing import Any

import pytest

from ai_review.services.vcs.types import (
    VCSClientProtocol,
    ReviewInfoSchema,
    ReviewThreadSchema,
    ReviewCommentSchema,
)


class FakeVCSClient(VCSClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []
        self.responses = responses or {}

    async def get_review_info(self) -> ReviewInfoSchema:
        self.calls.append(("get_review_info", (), {}))
        return self.responses.get(
            "get_review_info",
            ReviewInfoSchema(changed_files=["file.py"], base_sha="A", head_sha="B")
        )

    async def get_general_comments(self) -> list[ReviewCommentSchema]:
        self.calls.append(("get_general_comments", (), {}))
        return self.responses.get("get_general_comments", [])

    async def get_inline_comments(self) -> list[ReviewCommentSchema]:
        self.calls.append(("get_inline_comments", (), {}))
        return self.responses.get("get_inline_comments", [])

    async def create_general_comment(self, message: str) -> None:
        self.calls.append(("create_general_comment", (message,), {}))
        if error := self.responses.get("create_general_comment_error"):
            raise error

        return self.responses.get("create_general_comment_result", None)

    async def create_inline_comment(self, file: str, line: int, message: str) -> None:
        self.calls.append(("create_inline_comment", (file, line, message), {}))
        if error := self.responses.get("create_inline_comment_error"):
            raise error

        return self.responses.get("create_inline_comment_result", None)

    async def create_inline_reply(self, thread_id: int | str, message: str) -> None:
        self.calls.append(("create_inline_reply", (thread_id, message), {}))
        if error := self.responses.get("create_inline_reply_error"):
            raise error

        return self.responses.get("create_inline_reply_result", None)

    async def create_summary_reply(self, thread_id: int | str, message: str) -> None:
        self.calls.append(("create_summary_reply", (thread_id, message), {}))
        if error := self.responses.get("create_summary_reply_error"):
            raise error

        return self.responses.get("create_summary_reply_result", None)

    async def get_inline_threads(self) -> list[ReviewThreadSchema]:
        self.calls.append(("get_inline_threads", (), {}))
        return self.responses.get("get_inline_threads", [])

    async def get_general_threads(self) -> list[ReviewThreadSchema]:
        self.calls.append(("get_general_threads", (), {}))
        return self.responses.get("get_general_threads", [])


@pytest.fixture
def fake_vcs_client() -> FakeVCSClient:
    return FakeVCSClient()
