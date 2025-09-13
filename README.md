# AI Review

AI-powered code review tool.

---

## 🚀 Quick Start (GitLab CI)

Add the following to your `.gitlab-ci.yml`:

```yaml
ai-review:
  when: manual
  image: nikitafilonov/ai-review:latest
  stage: checks
  rules:
    - if: '$CI_MERGE_REQUEST_IID'
  script:
    - ai-review run
  variables:
    # LLM
    LLM__PROVIDER: "OPENAI"
    LLM__META__MODEL: "gpt-4o-mini"
    LLM__META__MAX_TOKENS: "1200"
    LLM__META__TEMPERATURE: "0.3"
    LLM__HTTP_CLIENT__API_URL: "https://api.openai.com/v1"
    LLM__HTTP_CLIENT__API_TOKEN: "$OPENAI_API_KEY"

    # VCS
    VCS__PROVIDER: "GITLAB"
    VCS__HTTP_CLIENT__API_URL: "$CI_SERVER_URL"
    VCS__HTTP_CLIENT__API_TOKEN: "$CI_JOB_TOKEN"
    VCS__PIPELINE__PROJECT_ID: "$CI_PROJECT_ID"
    VCS__PIPELINE__MERGE_REQUEST_ID: "$CI_MERGE_REQUEST_IID"

    # Prompts
    PROMPT__INLINE_PROMPT_FILE: "./prompts/inline.md"
    PROMPT__SUMMARY_PROMPT_FILE: "./prompts/summary.md"

    # Review
    REVIEW__MODE: "CHANGED_WITH_CONTEXT"
    REVIEW__CONTEXT_LINES: "10"
    REVIEW__REVIEW_CHANGE_MARKER: "# changed"
  allow_failure: true
```

This will:

- Run AI review on every Merge Request.
- Post inline + summary comments directly into the MR.
- **Run manually by default (`when: manual`)**, so it never breaks your pipeline.

---

## 🔑 Setup

1. Go to `GitLab` → `Settings` → `CI/CD` → `Variables`
2. Add your LLM API key (e.g. OpenAI):

```text
Key: OPENAI_API_KEY
Value: sk-your-token-here
Masked: ✅
```

You can also directly set `LLM__HTTP_CLIENT__API_TOKEN` if you prefer explicit configuration.

⚠️ Note: If you are using Gemini or Claude, replace `OPENAI_API_KEY` with `GEMINI_API_KEY` or `CLAUDE_API_KEY`
and adjust `LLM__PROVIDER` + `LLM__HTTP_CLIENT__API_URL` accordingly.

That’s it. Push your MR → click "Run pipeline" → trigger ai-review job.
You’ll see AI comments appear directly in the MR.

---

## ⚙️ Configuration (optional)

You can customize via `.ai-review.yaml`, `.ai-review.json`, or `.env`. See [./docs/configs](./docs/configs) for full
examples.

Examples of what you can configure:

- LLM provider (OpenAI/Gemini/Claude)
- Model, temperature, max tokens
- File review policy (allow/ignore)
- Custom prompts for inline/summary review

Defaults are already set to work out-of-the-box in GitLab CI.

---

## 🛠 Advanced usage

All base job templates are defined in [./docs/ci/gitlab/base.yaml](./docs/ci/gitlab/base.yaml).

You can extend them to run only inline or only summary review:

```yaml
ai-review-inline:
  extends: .ai-review-inline

ai-review-summary:
  extends: .ai-review-summary
```

---

## 📦 Docker Hub

The latest image is always available here: [nikitafilonov/ai-review](https://hub.docker.com/r/nikitafilonov/ai-review)

```shell
docker pull nikitafilonov/ai-review:latest
```

---

## 📂 Examples

- [./docs/ci/gitlab.yaml](./docs/ci/gitlab.yaml) — ready-to-use CI snippet
- [./docs/configs](./docs/configs) — sample `.yaml`, `.json`, `.env` configs
- [./docs/prompts](./docs/prompts) — prompt templates for Python/Go (light & strict modes)