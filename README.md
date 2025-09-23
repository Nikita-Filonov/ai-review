# AI Review

AI-powered code review tool.

_Made with ❤️ by [@NikitaFilonov](https://t.me/sound_right)_

---

## 📑 Table of Contents

- 🚀 [Quick Start](#-quick-start)
- ⚙️ [Configuration](#-configuration)
- 🛠 [Advanced usage](#-advanced-usage)
- 📂 [Examples](#-examples)

---

## 🚀 Quick Start

Install via **pip**:

```bash
pip install xai-review
```

Or run directly via Docker:

```bash
docker run --rm -v $(pwd):/app nikitafilonov/ai-review:latest run-summary
```

👉 Before running, create a basic configuration file [.ai-review.yaml](./docs/configs/.ai-review.yaml) in the root of
your project:

```yaml
llm:
  provider: OPENAI

  meta:
    model: gpt-4o-mini
    max_tokens: 1200
    temperature: 0.3

  http_client:
    timeout: 120
    api_url: https://api.openai.com/v1
    api_token: ${OPENAI_API_KEY}

vcs:
  provider: GITLAB

  pipeline:
    project_id: 1
    merge_request_id: 100

  http_client:
    timeout: 120
    api_url: https://gitlab.com
    api_token: ${GITLAB_API_TOKEN}
```

👉 This will:

- Run AI Review against your codebase.
- Generate inline and/or summary comments (depending on the selected mode).
- Use your chosen LLM provider (e.g., OpenAI GPT-4o-mini by default in this example).

> **Note:** Running `ai-review run` executes the full review (inline + summary).
> To run only one mode, use the dedicated subcommands:
> - ai-review run-inline
> - ai-review run-summary
> - ai-review run-context

---

AI Review can be configured via `.ai-review.yaml`, `.ai-review.json`, or `.env`. See [./docs/configs](./docs/configs)
for complete, ready-to-use examples.

Key things you can customize:

- **LLM provider** — OpenAI, Gemini, or Claude
- **Model settings** — model name, temperature, max tokens
- **VCS integration** — GitLab (currently supported) with project/MR context
- **Review policy** — which files to include/exclude, review modes
- **Prompts** — inline/context/summary prompt templates

👉 Minimal configuration is enough to get started. Use the full reference configs if you want fine-grained control (
timeouts, artifacts, logging, etc.).

---

## 🛠 Advanced usage

Below is the **full configuration reference** with all available options. Most projects only need a
minimal `.ai-review.yaml`, but you can use these templates as a starting point for advanced setups:

- [docs/configs/.ai-review.yaml](./docs/configs/.ai-review.yaml) — YAML configuration (with comments)
- [docs/configs/.ai-review.json](./docs/configs/.ai-review.json) — JSON configuration
- [docs/configs/.env.example](./docs/configs/.env.example) — environment variables example

👉 The YAML file includes comments for every option, making it the best place to explore the complete set of settings.

Below is an **example GitLab CI job** showing how to run AI Review with these variables:

```yaml
ai-review:
  tags: [ build ]
  when: manual
  stage: checks
  image: nikitafilonov/ai-review:latest
  rules:
    - if: '$CI_MERGE_REQUEST_IID'
  script:
    - ai-review run
  variables:
    # ===============================
    # LLM provider & model
    # ===============================
    # Which LLM to use.
    # Options: OPENAI | GEMINI | CLAUDE
    LLM__PROVIDER: "OPENAI"

    # --- Model metadata ---
    # For OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
    # For Gemini: gemini-2.0-pro, gemini-2.0-flash
    # For Claude: claude-3-opus, claude-3-sonnet, claude-3-haiku
    LLM__META__MODEL: "gpt-4o-mini"

    # Max tokens for completion.
    LLM__META__MAX_TOKENS: "1200"

    # Creativity of responses (0 = deterministic, >0 = more creative).
    LLM__META__TEMPERATURE: "0.3"

    # --- HTTP client configuration ---
    # API endpoint + token (must be set as CI/CD variables).
    LLM__HTTP_CLIENT__API_URL: "https://api.openai.com/v1"
    LLM__HTTP_CLIENT__API_TOKEN: "$OPENAI_API_KEY"

    # Example for Gemini:
    # LLM__HTTP_CLIENT__API_URL: "https://generativelanguage.googleapis.com"
    # LLM__HTTP_CLIENT__API_TOKEN: "$GEMINI_API_KEY"

    # Example for Claude:
    # LLM__HTTP_CLIENT__API_URL: "https://api.anthropic.com"
    # LLM__HTTP_CLIENT__API_TOKEN: "$CLAUDE_API_KEY"
    # LLM__HTTP_CLIENT__API_VERSION: "2023-06-01"

    # ===============================
    # VCS (GitLab integration)
    # ===============================
    VCS__PROVIDER: "GITLAB"

    # Context of the current pipeline (auto-populated by GitLab).
    VCS__PIPELINE__PROJECT_ID: "$CI_PROJECT_ID"
    VCS__PIPELINE__MERGE_REQUEST_ID: "$CI_MERGE_REQUEST_IID"

    # GitLab API access.
    VCS__HTTP_CLIENT__API_URL: "$CI_SERVER_URL"
    VCS__HTTP_CLIENT__API_TOKEN: "$CI_JOB_TOKEN"

    # ===============================
    # Prompts (optional overrides)
    # ===============================
    # Inline prompts (joined in order, local review instructions).
    # PROMPT__INLINE_PROMPT_FILES__0: "./prompts/inline.md"

    # Inline system prompts (format/contract rules).
    # PROMPT__SYSTEM_INLINE_PROMPT_FILES__0: "./prompts/system_inline.md"
    # PROMPT__INCLUDE_INLINE_SYSTEM_PROMPTS: "true"

    # Context prompts (joined in order, broader analysis instructions).
    # PROMPT__CONTEXT_PROMPT_FILES__0: "./prompts/context.md"

    # Context system prompts (format/contract rules).
    # PROMPT__SYSTEM_CONTEXT_PROMPT_FILES__0: "./prompts/system_context.md"
    # PROMPT__INCLUDE_CONTEXT_SYSTEM_PROMPTS: "true"

    # Summary prompts (joined in order, local review instructions).
    # PROMPT__SUMMARY_PROMPT_FILES__0: "./prompts/summary.md"

    # Summary system prompts (format/contract rules).
    # PROMPT__SYSTEM_SUMMARY_PROMPT_FILES__0: "./prompts/system_summary.md"
    # PROMPT__INCLUDE_SUMMARY_SYSTEM_PROMPTS: "true"

    # ===============================
    # Custom context variables
    # ===============================
    # You can inject custom variables into prompts via PROMPT__CONTEXT__*.
    # These will be available in all templates through placeholders.
    #
    # Placeholder syntax is defined separately in PROMPT__CONTEXT_PLACEHOLDER.
    # Default: <<{value}>>
    #
    # Example usage in prompt templates:
    #   Project: <<company_name>>
    #   Env: <<environment>>
    #   Pipeline: <<ci_pipeline_url>>
    #
    # Values override built-in variables if names collide.
    # To avoid clashes, prefer namespaced keys
    # (ci_pipeline_url, org_notify_handle, env_name).
    #
    # PROMPT__CONTEXT__ENVIRONMENT: "staging"
    # PROMPT__CONTEXT__COMPANY_NAME: "ACME Corp"
    # PROMPT__CONTEXT__CI_PIPELINE_URL: "https://gitlab.com/pipelines/123"
    #
    # ===============================
    # Context placeholder
    # ===============================
    # Defines how placeholders are written in prompt templates.
    # Must contain "{value}" which will be replaced by the variable name.
    #
    # Default: <<{value}>>
    #
    # Example:
    #   PROMPT__CONTEXT_PLACEHOLDER: "<<{value}>>"
    #   Template: "Env: <<environment>>"
    #   Result:   "Env: staging"
    #
    # PROMPT__CONTEXT_PLACEHOLDER: "<<{value}>>"

    # ===============================
    # Review options
    # ===============================
    # Available modes:
    #   FULL_FILE_DIFF
    #   FULL_FILE_CURRENT
    #   FULL_FILE_PREVIOUS
    #   ONLY_ADDED
    #   ONLY_REMOVED
    #   ADDED_AND_REMOVED
    #   ONLY_ADDED_WITH_CONTEXT
    #   ONLY_REMOVED_WITH_CONTEXT
    #   ADDED_AND_REMOVED_WITH_CONTEXT
    REVIEW__MODE: "FULL_FILE_DIFF"

    # Tags used to mark AI-generated comments in MR.
    REVIEW__INLINE_TAG: "#ai-review-inline"
    REVIEW__SUMMARY_TAG: "#ai-review-summary"

    # Context lines (only for *_WITH_CONTEXT modes).
    REVIEW__CONTEXT_LINES: "10"

    # Markers for changes in output.
    REVIEW__REVIEW_ADDED_MARKER: " # added"
    REVIEW__REVIEW_REMOVED_MARKER: " # removed"

    # Optional filters:
    # REVIEW__ALLOW_CHANGES: "src/*,lib/*"
    # REVIEW__IGNORE_CHANGES: "docs/*,README.md"

    # Optional limits for number of AI comments:
    # REVIEW__MAX_INLINE_COMMENTS: "20"   # Max inline comments per file (default: unlimited)
    # REVIEW__MAX_CONTEXT_COMMENTS: "50"  # Max context comments per MR (default: unlimited)

    # ===============================
    # Logger (optional)
    # ===============================
    LOGGER__LEVEL: "INFO"
    LOGGER__FORMAT: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[logger_name]} | {message}"

    # ===============================
    # Artifacts (optional)
    # ===============================
    ARTIFACTS__LLM_DIR: "./artifacts/llm"
    ARTIFACTS__LLM_ENABLED: "false"

  allow_failure: true

```

---

## 📂 Examples

- [./docs/ci](./docs/ci) — ready-to-use CI snippets
- [./docs/configs](./docs/configs) — sample `.yaml`, `.json`, `.env` configs
- [./docs/prompts](./docs/prompts) — prompt templates for Python/Go (light & strict modes)