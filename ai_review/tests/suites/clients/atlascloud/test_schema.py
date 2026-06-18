from ai_review.clients.atlascloud.schema import (
    AtlasCloudUsageSchema,
    AtlasCloudChoiceSchema,
    AtlasCloudMessageSchema,
    AtlasCloudChatRequestSchema,
    AtlasCloudChatResponseSchema,
)


# ---------- AtlasCloudChatResponseSchema ----------

def test_first_text_returns_text():
    resp = AtlasCloudChatResponseSchema(
        usage=AtlasCloudUsageSchema(total_tokens=5, prompt_tokens=2, completion_tokens=3),
        choices=[
            AtlasCloudChoiceSchema(
                message=AtlasCloudMessageSchema(role="assistant", content=" hello world ")
            )
        ],
    )
    assert resp.first_text == "hello world"


def test_first_text_empty_if_no_choices():
    resp = AtlasCloudChatResponseSchema(
        usage=AtlasCloudUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[],
    )
    assert resp.first_text == ""


def test_first_text_strips_and_handles_empty_content():
    resp = AtlasCloudChatResponseSchema(
        usage=AtlasCloudUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[
            AtlasCloudChoiceSchema(
                message=AtlasCloudMessageSchema(role="assistant", content="   ")
            )
        ],
    )
    assert resp.first_text == ""


# ---------- AtlasCloudChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    msg = AtlasCloudMessageSchema(role="user", content="hello")
    req = AtlasCloudChatRequestSchema(
        model="deepseek-ai/deepseek-v4-pro",
        messages=[msg],
        max_tokens=100,
        temperature=0.3,
    )
    assert req.model == "deepseek-ai/deepseek-v4-pro"
    assert req.messages[0].content == "hello"
    assert req.max_tokens == 100
    assert req.temperature == 0.3
