from ai_review.clients.ollama.schema import (
    OllamaMessageSchema,
    OllamaOptionsSchema,
    OllamaChatRequestSchema,
    OllamaUsageSchema,
    OllamaChatResponseSchema,
)


# ---------- OllamaUsageSchema ----------

def test_usage_total_tokens_sum_ok():
    usage = OllamaUsageSchema(prompt_tokens=5, completion_tokens=7)
    assert usage.total_tokens == 12


def test_usage_total_tokens_none_if_missing():
    usage = OllamaUsageSchema(prompt_tokens=3)
    assert usage.total_tokens is None


# ---------- OllamaChatResponseSchema ----------

def test_first_text_returns_text():
    resp = OllamaChatResponseSchema(
        model="llama2",
        message=OllamaMessageSchema(role="assistant", content=" hello ollama "),
        usage=OllamaUsageSchema(prompt_tokens=2, completion_tokens=3),
    )
    assert resp.first_text == "hello ollama"


def test_first_text_empty_if_content_empty():
    resp = OllamaChatResponseSchema(
        model="llama2",
        message=OllamaMessageSchema(role="assistant", content="   "),
        usage=OllamaUsageSchema(prompt_tokens=1, completion_tokens=1),
    )
    assert resp.first_text == ""


# ---------- OllamaChatRequestSchema ----------

def test_chat_request_schema_builds_ok():
    msg = OllamaMessageSchema(role="user", content="hi ollama")
    opts = OllamaOptionsSchema(
        stop=["stop1", "stop2"],
        seed=123,
        top_p=0.9,
        temperature=0.7,
        num_predict=256,
        repeat_penalty=1.1,
    )
    req = OllamaChatRequestSchema(
        model="llama2",
        stream=False,
        options=opts,
        messages=[msg],
    )

    assert req.model == "llama2"
    assert req.options.temperature == 0.7
    assert req.options.num_predict == 256
    assert req.options.stop == ["stop1", "stop2"]
    assert req.messages[0].content == "hi ollama"
