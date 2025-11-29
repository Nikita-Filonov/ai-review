from ai_review.clients.bedrock.schema import (
    BedrockUsageSchema,
    BedrockMessageSchema,
    BedrockContentSchema,
    BedrockChatRequestSchema,
    BedrockChatResponseSchema,
)


# ---------- BedrockChatResponseSchema ----------

def test_first_text_returns_text():
    resp = BedrockChatResponseSchema(
        id="fake-id",
        type="message",
        role="assistant",
        usage=BedrockUsageSchema(input_tokens=3, output_tokens=7),
        content=[BedrockContentSchema(type="text", text=" hello bedrock ")],
    )
    assert resp.first_text == "hello bedrock"


def test_first_text_empty_if_no_content():
    resp = BedrockChatResponseSchema(
        id="fake-id",
        type="message",
        role="assistant",
        usage=BedrockUsageSchema(input_tokens=1, output_tokens=1),
        content=[],
    )
    assert resp.first_text == ""


def test_first_text_strips_and_handles_empty_content():
    resp = BedrockChatResponseSchema(
        id="fake-id",
        type="message",
        role="assistant",
        usage=BedrockUsageSchema(input_tokens=1, output_tokens=1),
        content=[BedrockContentSchema(type="text", text="   ")],
    )
    assert resp.first_text == ""


# ---------- BedrockChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    msg = BedrockMessageSchema(role="user", content="hello")
    req = BedrockChatRequestSchema(
        messages=[msg],
        system="system prompt",
        max_tokens=128,
        temperature=0.7,
    )

    assert req.messages[0].role == "user"
    assert req.messages[0].content == "hello"
    assert req.system == "system prompt"
    assert req.max_tokens == 128
    assert req.temperature == 0.7


# ---------- BedrockUsageSchema ----------

def test_usage_total_tokens_calculates_correctly():
    usage = BedrockUsageSchema(input_tokens=10, output_tokens=20)
    assert usage.total_tokens == 30
