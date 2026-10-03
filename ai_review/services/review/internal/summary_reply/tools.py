import re
from urllib.parse import quote, unquote


def format_summary_reply_reference(thread_id: str | int, comment_id: str | int) -> str:
    """Persist the answered request in the reply, including thread-scoped comment IDs."""
    thread = quote(str(thread_id), safe="")
    comment = quote(str(comment_id), safe="")
    return f"<!-- ai-review:summary-reply thread={thread} comment={comment} -->"


def get_summary_reply_reference(body: str) -> tuple[str, str] | None:
    """Read the generated footer; quoted markers elsewhere are not acknowledgements."""
    match = re.search(
        r"(?:^|\n)<!-- ai-review:summary-reply thread=(\S+) comment=(\S+) -->\s*\Z",
        body,
    )
    if not match:
        return None

    return unquote(match[1]), unquote(match[2])
