from ai_review.clients.llmtr.schema import (
    LLMTRUsageSchema,
    LLMTRChoiceSchema,
    LLMTRMessageSchema,
    LLMTRChatRequestSchema,
    LLMTRChatResponseSchema,
)


# ---------- LLMTRChatResponseSchema ----------

def test_first_text_returns_text():
    resp = LLMTRChatResponseSchema(
        usage=LLMTRUsageSchema(total_tokens=5, prompt_tokens=2, completion_tokens=3),
        choices=[
            LLMTRChoiceSchema(
                message=LLMTRMessageSchema(role="assistant", content=" hello world ")
            )
        ],
    )
    assert resp.first_text == "hello world"


def test_first_text_empty_if_no_choices():
    resp = LLMTRChatResponseSchema(
        usage=LLMTRUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[],
    )
    assert resp.first_text == ""


def test_first_text_strips_and_handles_empty_content():
    resp = LLMTRChatResponseSchema(
        usage=LLMTRUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[
            LLMTRChoiceSchema(
                message=LLMTRMessageSchema(role="assistant", content="   ")
            )
        ],
    )
    assert resp.first_text == ""


# ---------- LLMTRChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    msg = LLMTRMessageSchema(role="user", content="hello")
    req = LLMTRChatRequestSchema(
        model="qwen/qwen3.8-27b-free",
        messages=[msg],
        max_tokens=100,
        temperature=0.3,
    )
    assert req.model == "qwen/qwen3.8-27b-free"
    assert req.messages[0].content == "hello"
    assert req.max_tokens == 100
    assert req.temperature == 0.3
