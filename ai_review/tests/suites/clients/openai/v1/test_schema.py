from ai_review.clients.openai.v1.schema import (
    OpenAIUsageSchema,
    OpenAIMessageSchema,
    OpenAIChoiceSchema,
    OpenAIChatRequestSchema,
    OpenAIChatResponseSchema,
)


# ---------- OpenAIChatResponseSchema ----------

def test_first_text_returns_text():
    resp = OpenAIChatResponseSchema(
        usage=OpenAIUsageSchema(total_tokens=5, prompt_tokens=2, completion_tokens=3),
        choices=[
            OpenAIChoiceSchema(
                message=OpenAIMessageSchema(role="assistant", content=" hello world ")
            )
        ],
    )
    assert resp.first_text == "hello world"


def test_first_text_empty_if_no_choices():
    resp = OpenAIChatResponseSchema(
        usage=OpenAIUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[],
    )
    assert resp.first_text == ""


def test_first_text_strips_and_handles_empty_content():
    resp = OpenAIChatResponseSchema(
        usage=OpenAIUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[OpenAIChoiceSchema(message=OpenAIMessageSchema(role="assistant", content="   "))],
    )
    assert resp.first_text == ""


# ---------- OpenAIChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    msg = OpenAIMessageSchema(role="user", content="hello")
    req = OpenAIChatRequestSchema(
        model="gpt-4o-mini",
        messages=[msg],
        max_tokens=100,
        temperature=0.3,
    )
    assert req.model == "gpt-4o-mini"
    assert req.messages[0].content == "hello"
    assert req.max_tokens == 100
    assert req.temperature == 0.3
