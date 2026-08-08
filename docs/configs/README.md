# 📘 AI Review Configuration

AI Review supports multiple configuration formats and sources. All of them are automatically detected at runtime.

---

## 📂 Supported formats

- **YAML** (recommended): `.ai-review.yaml`
- **JSON**: `.ai-review.json`
- **ENV**: `.env`

👉 You can combine formats: values are loaded in order of priority.

---

## 📑 Load priority

1. **YAML** (`.ai-review.yaml` or path from `AI_REVIEW_CONFIG_FILE_YAML`)
2. **JSON** (`.ai-review.json` or path from `AI_REVIEW_CONFIG_FILE_JSON`)
3. **ENV** (`.env` or path from `AI_REVIEW_CONFIG_FILE_ENV`)
4. **Environment variables** (`LLM__PROVIDER=OPENAI`, etc.)
5. **Initialization arguments** (if used as a library)

---

## ⚙️ Override file paths

You can override default config locations using environment variables:

- `AI_REVIEW_CONFIG_FILE_YAML` — path to `.yaml` config
- `AI_REVIEW_CONFIG_FILE_JSON` — path to `.json` config
- `AI_REVIEW_CONFIG_FILE_ENV` — path to `.env`

By default, configs are loaded from the **project root**.

---

## 📘 Examples

- [.ai-review.yaml](./.ai-review.yaml) — main YAML config with comments
- [.ai-review.json](./.ai-review.json) — JSON config example
- [.env.example](./.env.example) — ENV config example

---

## 🧠 OpenAI reasoning

OpenAI reasoning options can be configured for models that use the Responses API. The object is optional and is omitted
from requests when it is not configured. It is not sent to models that use Chat Completions.

### YAML

```yaml
llm:
  provider: OPENAI
  meta:
    model: gpt-5.6-sol
    reasoning:
      effort: medium
      summary: concise
      context: all_turns
      mode: standard
```

### JSON

```json
{
  "llm": {
    "provider": "OPENAI",
    "meta": {
      "model": "gpt-5.6-sol",
      "reasoning": {
        "effort": "medium",
        "summary": "concise",
        "context": "all_turns",
        "mode": "standard"
      }
    }
  }
}
```

### Environment variables

```dotenv
LLM__PROVIDER=OPENAI
LLM__META__MODEL=gpt-5.6-sol
LLM__META__REASONING__EFFORT=medium
LLM__META__REASONING__SUMMARY=concise
LLM__META__REASONING__CONTEXT=all_turns
LLM__META__REASONING__MODE=standard
```

### Options

| Option | Supported values | Description |
|---|---|---|
| `effort` | `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max` | Controls how many reasoning tokens the model uses. Not every model supports every value. |
| `summary` | `auto`, `concise`, `detailed` | Requests a summary of the model reasoning. |
| `context` | `auto`, `current_turn`, `all_turns` | Controls which reasoning items are provided to the model on later turns. |
| `mode` | `standard`, `pro` | Selects the reasoning execution mode. Model support may vary. |
| `generate_summary` | `auto`, `concise`, `detailed` | Deprecated OpenAI option. Use `summary` instead. |

See the [OpenAI Responses API reference](https://developers.openai.com/api/reference/resources/responses/methods/create/#reasoning)
for model-specific support and current behavior.

---

## 🔍 Tips

- Use **YAML** for most projects — it’s human-friendly and supports comments.
- **JSON** is convenient for automation (e.g., CI/CD pipelines).
- **ENV** is useful for local development and quick overrides.
