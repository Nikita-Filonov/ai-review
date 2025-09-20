from ai_review.libs.diff.models import DiffLineType


def is_source_line(line: str) -> bool:
    if line == r"\ No newline at end of file":
        return False
    if not line or line.startswith("---") or line.startswith("+++"):
        return False
    return True


def get_line_type(line: str) -> DiffLineType:
    if not line:
        raise ValueError("Empty line cannot be classified as DiffLineType")

    match line[0]:
        case "+":
            return DiffLineType.ADDED
        case "-":
            return DiffLineType.REMOVED
        case " ":
            return DiffLineType.UNCHANGED
        case _:
            raise ValueError(f"Unknown diff line prefix: {line!r}")
