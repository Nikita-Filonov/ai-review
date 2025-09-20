from ai_review.clients.gemini.schema import (
    GeminiPartSchema,
    GeminiUsageSchema,
    GeminiContentSchema,
    GeminiCandidateSchema,
    GeminiGenerationConfigSchema,
    GeminiChatRequestSchema,
    GeminiChatResponseSchema,
)


# ---------- GeminiUsageSchema ----------

def test_usage_total_tokens_prefers_total_tokens_count():
    usage = GeminiUsageSchema(
        prompt_token_count=10,
        total_tokens_count=99,
        candidates_token_count=5,
        output_thoughts_token_count=3,
    )
    assert usage.total_tokens == 99  # приоритет у totalTokenCount


def test_usage_total_tokens_falls_back_to_sum():
    usage = GeminiUsageSchema(
        prompt_token_count=10,
        candidates_token_count=5,
        output_thoughts_token_count=3,
    )
    # 10 + 5 + 3
    assert usage.total_tokens == 18


def test_usage_prompt_tokens_and_completion_from_candidates():
    usage = GeminiUsageSchema(
        prompt_token_count=7,
        candidates_token_count=2,
    )
    assert usage.prompt_tokens == 7
    assert usage.completion_tokens == 2


def test_usage_completion_tokens_from_output_thoughts():
    usage = GeminiUsageSchema(
        prompt_token_count=7,
        output_thoughts_token_count=5,
    )
    assert usage.completion_tokens == 5


def test_usage_completion_tokens_none_if_not_provided():
    usage = GeminiUsageSchema(prompt_token_count=7)
    assert usage.completion_tokens is None


# ---------- GeminiChatResponseSchema ----------

def test_first_text_returns_text():
    resp = GeminiChatResponseSchema(
        usage=GeminiUsageSchema(prompt_token_count=3, total_tokens_count=5),
        candidates=[
            GeminiCandidateSchema(
                content=GeminiContentSchema(
                    role="model",
                    parts=[GeminiPartSchema(text=" hello world ")],
                )
            )
        ],
    )
    assert resp.first_text == "hello world"


def test_first_text_empty_if_no_candidates():
    resp = GeminiChatResponseSchema(
        usage=GeminiUsageSchema(prompt_token_count=1, total_tokens_count=2),
        candidates=[],
    )
    assert resp.first_text == ""


def test_first_text_empty_if_parts_missing():
    resp = GeminiChatResponseSchema(
        usage=GeminiUsageSchema(prompt_token_count=1, total_tokens_count=2),
        candidates=[
            GeminiCandidateSchema(content=GeminiContentSchema(role="model", parts=[]))
        ],
    )
    assert resp.first_text == ""


# ---------- GeminiChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    content = GeminiContentSchema(role="user", parts=[GeminiPartSchema(text="hi")])
    gen_cfg = GeminiGenerationConfigSchema(temperature=0.5, max_output_tokens=128)

    req = GeminiChatRequestSchema(
        contents=[content],
        generation_config=gen_cfg,
        system_instruction=GeminiContentSchema(role="system", parts=[GeminiPartSchema(text="sys")]),
    )

    assert req.contents[0].parts[0].text == "hi"
    assert req.generation_config.max_output_tokens == 128
    assert req.system_instruction.parts[0].text == "sys"
