import pytest

from ai_review.services.review.internal.inline_reply.tools import INLINE_REPLY_MARKER, is_inline_reply


def test_generated_footer_identifies_inline_reply():
    assert is_inline_reply(f"Answer\n\n{INLINE_REPLY_MARKER}\n")


@pytest.mark.parametrize("body", [
    "Answer #ai-review-inline",
    f"> {INLINE_REPLY_MARKER}",
    f"```\n{INLINE_REPLY_MARKER}\n```",
    f"{INLINE_REPLY_MARKER}\nQuestion",
])
def test_quoted_or_nonterminal_marker_is_not_a_reply(body: str):
    assert not is_inline_reply(body)
