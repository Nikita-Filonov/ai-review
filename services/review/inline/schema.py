from typing import Self

from pydantic import BaseModel, Field, RootModel, field_validator

DedupKey = tuple[str, int, str]


class InlineCommentSchema(BaseModel):
    file: str = Field(min_length=1)
    line: int = Field(ge=1)
    comment: str = Field(min_length=1)

    @field_validator("file")
    def normalize_file(cls, value: str) -> str:
        value = value.strip().replace("\\", "/")
        return value.lstrip("/")

    @field_validator("comment")
    def normalize_comment(cls, value: str) -> str:
        return value.strip()

    @property
    def dedup_key(self) -> DedupKey:
        return self.file, self.line, self.comment.strip().lower()


class InlineCommentListSchema(RootModel[list[InlineCommentSchema]]):
    root: list[InlineCommentSchema]

    def dedupe(self) -> Self:
        results_map: dict[DedupKey, InlineCommentSchema] = {
            comment.dedup_key: comment for comment in self.root
        }

        return InlineCommentListSchema(root=list(results_map.values()))

    def filter(self, allowed_map: dict[str, set[int]] | None = None) -> Self:
        if not allowed_map:
            return InlineCommentListSchema(root=self.root.copy())

        results = [
            comment
            for comment in self.root
            if (comment.file in allowed_map) and (comment.line in allowed_map[comment.file])
        ]
        return InlineCommentListSchema(root=results)
