import re


INLINE_REPLY_MARKER = "<!-- ai-review:inline-reply -->"


def is_inline_reply(body: str) -> bool:
    """Only a generated footer, not a quoted marker, identifies an AI reply."""
    return re.search(r"(?:^|\n)<!-- ai-review:inline-reply -->\s*\Z", body) is not None
