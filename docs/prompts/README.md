# 📘 AI Review Prompts

This folder contains **ready-to-use prompt templates** for AI Review.
They extend the built-in global
prompts ([prompts/default_system_inline.md](../../ai_review/prompts/default_system_inline.md),
[prompts/default_system_summary.md](../../ai_review/prompts/default_system_summary.md),
[prompts/default_system_context.md](../../ai_review/prompts/default_system_context.md)) and define style & tone of the
review.

---

## 📂 Available Prompt Sets

| Language | Style  | Inline Prompt                                        | Summary Prompt                                         |
|----------|--------|------------------------------------------------------|--------------------------------------------------------|
| Python   | Light  | [inline_python_light.md](./inline_python_light.md)   | [summary_python_light.md](./summary_python_light.md)   |
| Python   | Strict | [inline_python_strict.md](./inline_python_strict.md) | [summary_python_strict.md](./summary_python_strict.md) |
| Go       | Light  | [inline_go_light.md](./inline_go_light.md)           | [summary_go_light.md](./summary_go_light.md)           |
| Go       | Strict | [inline_go_strict.md](./inline_go_strict.md)         | [summary_go_strict.md](./summary_go_strict.md)         |

---

## 🔧 How to use

In your `.ai-review.yaml`, point to the desired inline, context, and summary prompts.
Each section supports multiple files — they will be concatenated in order.

```yaml
prompt:
  inline_prompt_files:
    - ./docs/prompts/inline_python_light.md
  context_prompt_files:
    - ./docs/prompts/inline_python_light.md
  summary_prompt_files:
    - ./docs/prompts/summary_python_light.md
```

or, for a stricter Go review:

```yaml
prompt:
  inline_prompt_files:
    - ./docs/prompts/inline_go_strict.md
  context_prompt_files:
    - ./docs/prompts/inline_go_strict.md
  summary_prompt_files:
    - ./docs/prompts/summary_go_strict.md
```

## 📝 Notes

- System prompts (`default_system_inline.md`, `default_system_context.md`, `default_system_summary.md`) are always
  included unless disabled with `include_*_system_prompts: false`. They enforce correct output format (JSON / plain
  text).
- Project-specific prompts should only define style and tone — not the schema contract.
- You can **mix & match** (e.g., `inline_go_strict.md` with `summary_python_light.md`).
- Add your own style guides alongside these defaults (e.g., `./prompts/style.md`).

## 🔀 Prompt Formatting

Prompt templates support **placeholders**. The placeholder syntax is configurable via `prompt.context_placeholder` (
YAML/JSON) or `AI_REVIEW__PROMPT__CONTEXT_PLACEHOLDER` (ENV).

For example:

```text
Please review the changes in **<<merge_request_title>>**  
Author: @<<merge_request_author_username>>  
Labels: <<labels>>
```

### 📌 Available Variables

| Variable                     | Example                             | Description                                   |
|------------------------------|-------------------------------------|-----------------------------------------------|
| `review_title`               | `"Fix login bug"`                   | Review title (PR/MR title)                    |
| `review_description`         | `"Implements redirect after login"` | Review description (PR/MR description)        |
| `review_author_name`         | `"Nikita"`                          | Author’s display name                         |
| `review_author_username`     | `"nikita.filonov"`                  | Author’s username (use `@{...}` for mentions) |
| `review_reviewer`            | `"Alice"`                           | First reviewer’s name (if any)                |
| `review_reviewers`           | `"Alice, Bob"`                      | List of reviewers (names)                     |
| `review_reviewers_usernames` | `"alice, bob"`                      | List of reviewers (usernames)                 |
| `review_assignees`           | `"Charlie, Diana"`                  | List of assignees (names)                     |
| `review_assignees_usernames` | `"charlie, diana"`                  | List of assignees (usernames)                 |
| `source_branch`              | `"feature/login-fix"`               | Source branch                                 |
| `target_branch`              | `"main"`                            | Target branch                                 |
| `labels`                     | `"bug, critical"`                   | Review labels                                 |
| `changed_files`              | `"foo.py, bar.py"`                  | Changed files in review                       |

✅ This allows you to write conditional instructions directly in your prompt.

For example:

```text
If the title **<<review_title>>** does not include a ticket ID,
mention @<<review_author_username>> and ask to update it.

If <<labels>> do not contain "autotests",
remind @<<review_author_username>> to add it.
```

### 🔧 Custom Variables

In addition to the built-in variables, you can inject **your own context variables** into any prompt.

These are configured under `prompt.context` and can be provided via:

- **YAML** ([.ai-review.yaml](../../docs/configs/.ai-review.yaml))
- **JSON** ([.ai-review.json](../../docs/configs/.ai-review.json))
- **ENV variables** (`AI_REVIEW__PROMPT__CONTEXT__your_key=value`)
- **.env file** (same as ENV)

At runtime, all keys under `prompt.context` become placeholders available in prompt templates.

#### Example: YAML

```yaml
prompt:
  context:
    environment: "staging"
    company_name: "ACME Corp"
    ci_pipeline_url: "https://gitlab.com/pipelines/123"
```

#### Example: JSON

```json
{
  "prompt": {
    "context": {
      "environment": "staging",
      "company_name": "ACME Corp"
    }
  }
}
```

#### Example: ENV / .env

```dotenv
AI_REVIEW__PROMPT__CONTEXT__ENVIRONMENT="staging"
AI_REVIEW__PROMPT__CONTEXT__COMPANY_NAME="ACME Corp"
```

#### Usage in prompt templates

```text
Company: <<company_name>>
Environment: <<environment>>
Pipeline: <<ci_pipeline_url>>
Author: @<<review_author_username>>
```

### Notes

- All context keys are automatically merged into the built-in prompt variables.
- If a custom key overrides a built-in variable (e.g., `labels`), the custom value wins.
- To avoid clashes, prefer namespaced keys (e.g. `ci_pipeline_url`, `org_notify_handle`).
- Non-string values will be stringified automatically.