import re


def contains_tag(text: str, tag: str) -> bool:
    """Match a literal tag without matching a prefix of another tag."""
    if not tag:
        return False

    return re.search(rf"(?<![\w#-]){re.escape(tag)}(?![\w-])", text) is not None


def truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text

    omitted = len(text) - limit
    return f"{text[:limit]}\n\n... output truncated ({omitted} chars omitted)"
