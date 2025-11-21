from ai_review.clients.azure_openai.schema import (
    AzureOpenAIUsage,
    AzureOpenAIMessage,
    AzureOpenAITextBlock,
    AzureOpenAIChoice,
    AzureOpenAIChatQuerySchema,
    AzureOpenAIChatRequestSchema,
    AzureOpenAIChatResponseSchema,
)


# ----------------------------------------------------------------------
#                      AzureOpenAIUsage Tests
# ----------------------------------------------------------------------

def test_usage_fields_correct():
    usage = AzureOpenAIUsage(
        total_tokens=30,
        prompt_tokens=12,
        completion_tokens=18,
    )
    assert usage.total_tokens == 30
    assert usage.prompt_tokens == 12
    assert usage.completion_tokens == 18


# ----------------------------------------------------------------------
#                 AzureOpenAIChatResponseSchema.first_text Tests
# ----------------------------------------------------------------------

def test_first_text_returns_string_content():
    resp = AzureOpenAIChatResponseSchema(
        usage=AzureOpenAIUsage(
            total_tokens=10,
            prompt_tokens=3,
            completion_tokens=7
        ),
        choices=[
            AzureOpenAIChoice(
                index=0,
                finish_reason="stop",
                message=AzureOpenAIMessage(
                    role="assistant",
                    content=" hello azure "
                )
            )
        ],
    )

    assert resp.first_text == "hello azure"


def test_first_text_extracts_from_text_blocks():
    resp = AzureOpenAIChatResponseSchema(
        usage=AzureOpenAIUsage(
            total_tokens=10,
            prompt_tokens=3,
            completion_tokens=7
        ),
        choices=[
            AzureOpenAIChoice(
                index=0,
                finish_reason="stop",
                message=AzureOpenAIMessage(
                    role="assistant",
                    content=[
                        AzureOpenAITextBlock(type="text", text="hello "),
                        AzureOpenAITextBlock(type="text", text="azure "),
                        AzureOpenAITextBlock(type="text", text="world"),
                    ]
                )
            )
        ],
    )

    assert resp.first_text == "hello azure world"


def test_first_text_empty_if_no_choices():
    resp = AzureOpenAIChatResponseSchema(
        usage=AzureOpenAIUsage(total_tokens=5, prompt_tokens=2, completion_tokens=3),
        choices=[]
    )
    assert resp.first_text == ""


# ----------------------------------------------------------------------
#                      AzureOpenAIChatQuerySchema Tests
# ----------------------------------------------------------------------

def test_query_schema_serializes_with_alias():
    q = AzureOpenAIChatQuerySchema(api_version="2024-06-01")
    dumped = q.model_dump(by_alias=True)

    assert "api-version" in dumped
    assert dumped["api-version"] == "2024-06-01"


# ----------------------------------------------------------------------
#                      AzureOpenAIChatRequestSchema Tests
# ----------------------------------------------------------------------

def test_chat_request_schema_builds_ok():
    req = AzureOpenAIChatRequestSchema(
        messages=[
            AzureOpenAIMessage(role="system", content="sys msg"),
            AzureOpenAIMessage(role="user", content="hello"),
        ],
        max_tokens=500,
        temperature=0.4,
    )

    assert req.messages[0].role == "system"
    assert req.messages[1].content == "hello"
    assert req.max_tokens == 500
    assert req.temperature == 0.4
