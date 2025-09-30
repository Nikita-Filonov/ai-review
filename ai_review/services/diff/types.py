from typing import Protocol

from ai_review.libs.diff.models import Diff
from ai_review.services.diff.schema import DiffFileSchema
from ai_review.services.git.types import GitServiceProtocol


class DiffServiceProtocol(Protocol):
    def parse(self, raw_diff: str) -> Diff:
        ...

    def render_file(
            self,
            file: str,
            raw_diff: str,
            base_sha: str | None = None,
            head_sha: str | None = None,
    ) -> DiffFileSchema:
        ...

    def render_files(
            self,
            git: GitServiceProtocol,
            files: list[str],
            base_sha: str,
            head_sha: str,
    ) -> list[DiffFileSchema]:
        ...
