from enum import StrEnum
from typing import Self

from pydantic import BaseModel, RootModel


class DiffLineType(StrEnum):
    ADDED = "ADDED"
    DELETED = "DELETED"
    UNCHANGED = "UNCHANGED"


class DiffLineSchema(BaseModel):
    file: str
    line: int | None = None
    content: str
    line_type: DiffLineType


class DiffLineListSchema(RootModel[list[DiffLineSchema]]):
    root: list[DiffLineSchema]

    def filter(
            self,
            file: str | None = None,
            line_type: DiffLineType | None = None,
    ) -> Self:
        results = [
            diff_line
            for diff_line in self.root
            if (file is None or diff_line.file.lower() == file.lower()) and
               (line_type is None or diff_line.line_type == line_type)
        ]
        return DiffLineListSchema(root=results)

    def filter_only_added(self) -> Self:
        return self.filter(line_type=DiffLineType.ADDED)
