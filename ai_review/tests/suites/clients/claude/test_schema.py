from ai_review.clients.claude.schema import (
    ClaudeUsageSchema,
    ClaudeContentSchema,
    ClaudeMessageSchema,
    ClaudeChatRequestSchema,
    ClaudeChatResponseSchema,
)


# ---------- ClaudeUsageSchema ----------

def test_usage_total_tokens_property():
    usage = ClaudeUsageSchema(input_tokens=10, output_tokens=5)
    assert usage.total_tokens == 15


# ---------- ClaudeChatResponseSchema ----------

def test_first_text_returns_text():
    resp = ClaudeChatResponseSchema(
        id="123",
        role="assistant",
        usage=ClaudeUsageSchema(input_tokens=3, output_tokens=7),
        content=[
            ClaudeContentSchema(type="text", text=" hello world 1 "),
            ClaudeContentSchema(type="text", text=" hello world 2 "),
        ],
    )
    assert resp.first_text == "hello world 1"


def test_first_text_empty_if_no_content():
    resp = ClaudeChatResponseSchema(
        id="123",
        role="assistant",
        usage=ClaudeUsageSchema(input_tokens=1, output_tokens=2),
        content=[],
    )
    assert resp.first_text == ""


# ---------- ClaudeChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    msg = ClaudeMessageSchema(role="user", content="hello")
    req = ClaudeChatRequestSchema(
        model="claude-3-sonnet",
        system="You are a helpful assistant",
        messages=[msg],
        max_tokens=512,
        temperature=0.3,
    )

    assert req.model == "claude-3-sonnet"
    assert req.system == "You are a helpful assistant"
    assert req.messages[0].role == "user"
    assert req.messages[0].content == "hello"
    assert req.max_tokens == 512
    assert req.temperature == 0.3
