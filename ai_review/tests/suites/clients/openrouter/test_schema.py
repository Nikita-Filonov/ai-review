from ai_review.clients.openrouter.schema import (
    OpenRouterUsageSchema,
    OpenRouterChoiceSchema,
    OpenRouterMessageSchema,
    OpenRouterChatRequestSchema,
    OpenRouterChatResponseSchema,
)


# ---------- OpenRouterChatResponseSchema ----------

def test_first_text_returns_text():
    resp = OpenRouterChatResponseSchema(
        usage=OpenRouterUsageSchema(total_tokens=5, prompt_tokens=2, completion_tokens=3),
        choices=[
            OpenRouterChoiceSchema(
                message=OpenRouterMessageSchema(role="assistant", content=" hello world ")
            )
        ],
    )
    assert resp.first_text == "hello world"


def test_first_text_empty_if_no_choices():
    resp = OpenRouterChatResponseSchema(
        usage=OpenRouterUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[],
    )
    assert resp.first_text == ""


def test_first_text_strips_and_handles_empty_content():
    resp = OpenRouterChatResponseSchema(
        usage=OpenRouterUsageSchema(total_tokens=1, prompt_tokens=1, completion_tokens=0),
        choices=[
            OpenRouterChoiceSchema(
                message=OpenRouterMessageSchema(role="assistant", content="   ")
            )
        ],
    )
    assert resp.first_text == ""


# ---------- OpenRouterChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    msg = OpenRouterMessageSchema(role="user", content="hello")
    req = OpenRouterChatRequestSchema(
        model="gpt-4o-mini",
        messages=[msg],
        max_tokens=100,
        temperature=0.3,
    )
    assert req.model == "gpt-4o-mini"
    assert req.messages[0].content == "hello"
    assert req.max_tokens == 100
    assert req.temperature == 0.3
