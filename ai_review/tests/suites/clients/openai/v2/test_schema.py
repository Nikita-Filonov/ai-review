import pytest
from pydantic import ValidationError

from ai_review.clients.openai.v2.schema import (
    OpenAIResponseUsageSchema,
    OpenAIInputMessageSchema,
    OpenAIResponseContentSchema,
    OpenAIResponseOutputSchema,
    OpenAIReasoningSchema,
    OpenAIResponsesRequestSchema,
    OpenAIResponsesResponseSchema,
)


# ---------- OpenAIResponsesResponseSchema ----------

def test_first_text_returns_combined_text():
    resp = OpenAIResponsesResponseSchema(
        usage=OpenAIResponseUsageSchema(total_tokens=42, input_tokens=21, output_tokens=21),
        output=[
            OpenAIResponseOutputSchema(
                type="message",
                role="assistant",
                content=[
                    OpenAIResponseContentSchema(type="output_text", text="Hello"),
                    OpenAIResponseContentSchema(type="output_text", text=" World"),
                ],
            )
        ],
    )

    assert resp.first_text == "Hello World"


def test_first_text_empty_if_no_output():
    resp = OpenAIResponsesResponseSchema(
        usage=OpenAIResponseUsageSchema(total_tokens=0, input_tokens=0, output_tokens=0),
        output=[],
    )
    assert resp.first_text == ""


def test_first_text_ignores_non_message_blocks():
    resp = OpenAIResponsesResponseSchema(
        usage=OpenAIResponseUsageSchema(total_tokens=5, input_tokens=2, output_tokens=3),
        output=[
            OpenAIResponseOutputSchema(
                type="reasoning",  # игнорируется
                role=None,
                content=None,
            )
        ],
    )
    assert resp.first_text == ""


# ---------- OpenAIResponsesRequestSchema ----------

def test_responses_request_schema_builds_ok():
    msg = OpenAIInputMessageSchema(role="user", content="hello")
    req = OpenAIResponsesRequestSchema(
        model="gpt-5",
        input=[msg],
        temperature=0.2,
        max_output_tokens=512,
        instructions="You are a helpful assistant.",
    )

    assert req.model == "gpt-5"
    assert req.input[0].role == "user"
    assert req.input[0].content == "hello"
    assert req.temperature == 0.2
    assert req.max_output_tokens == 512
    assert req.instructions == "You are a helpful assistant."


def test_responses_request_schema_allows_none_tokens():
    req = OpenAIResponsesRequestSchema(
        model="gpt-5",
        input=[OpenAIInputMessageSchema(role="user", content="test")],
    )

    dumped = req.model_dump(exclude_none=True)
    assert "max_output_tokens" not in dumped


def test_responses_request_schema_includes_reasoning_object():
    req = OpenAIResponsesRequestSchema(
        model="gpt-5.6-sol",
        input=[OpenAIInputMessageSchema(role="user", content="test")],
        reasoning={
            "effort": "medium",
            "summary": "concise",
            "context": "all_turns",
            "mode": "pro",
            "generate_summary": "detailed",
        },
    )

    assert req.model_dump(exclude_none=True)["reasoning"] == {
        "effort": "medium",
        "summary": "concise",
        "context": "all_turns",
        "mode": "pro",
        "generate_summary": "detailed",
    }


def test_responses_request_schema_omits_reasoning_by_default():
    req = OpenAIResponsesRequestSchema(
        model="gpt-5",
        input=[OpenAIInputMessageSchema(role="user", content="test")],
    )

    assert "reasoning" not in req.model_dump(exclude_none=True)


@pytest.mark.parametrize(
    "reasoning",
    [
        {"effort": "invalid"},
        {"summary": "invalid"},
        {"context": "invalid"},
        {"mode": "invalid"},
        {"unknown_option": True},
    ],
)
def test_reasoning_schema_rejects_invalid_contract(reasoning: dict):
    with pytest.raises(ValidationError):
        OpenAIReasoningSchema(**reasoning)


def test_responses_request_schema_stream_defaults_to_false():
    msg = OpenAIInputMessageSchema(role="user", content="hi")
    req = OpenAIResponsesRequestSchema(model="gpt-5", input=[msg])
    assert req.stream is False


def test_responses_request_schema_stream_included_in_payload():
    msg = OpenAIInputMessageSchema(role="user", content="hi")
    req = OpenAIResponsesRequestSchema(model="gpt-5", input=[msg])
    payload = req.model_dump(exclude_none=True)
    assert payload["stream"] is False
