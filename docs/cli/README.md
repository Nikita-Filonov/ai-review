# 📘 AI Review CLI

The **AI Review CLI** provides a simple interface to run reviews, inspect configuration, and integrate with CI/CD
pipelines.

It is built with Typer and fully supports async execution of all review modes.

---

## 🚀 Quick Start

After installing AI Review:

````bash
pip install xai-review
````

Run any command from your terminal:

```bash
ai-review run
```

Or display help:

```bash
ai-review --help
```

---

## 🧩 Available Commands

| Command                       | Description                                                               | Typical Usage                 |
|-------------------------------|---------------------------------------------------------------------------|-------------------------------|
| `ai-review run`               | Runs the full review pipeline (inline + summary).                         | `ai-review run`               |
| `ai-review run-inline`        | Runs only **inline review** (line-by-line comments).                      | `ai-review run-inline`        |
| `ai-review run-context`       | Runs **context review** across multiple files for architectural feedback. | `ai-review run-context`       |
| `ai-review run-summary`       | Runs **summary review** that posts a single summarizing comment.          | `ai-review run-summary`       |
| `ai-review run-inline-reply`  | Generates **AI replies** to existing inline comment threads.              | `ai-review run-inline-reply`  |
| `ai-review run-summary-reply` | Generates **AI replies** to existing summary review threads.              | `ai-review run-summary-reply` |
| `ai-review clear-inline`      | Removes all **AI-generated inline comments** from the review.             | `ai-review clear-inline`      |
| `ai-review clear-summary`     | Removes all **AI-generated summary comments** from the review.            | `ai-review clear-summary`     |
| `ai-review show-config`       | Prints the currently resolved configuration (merged from YAML/JSON/ENV).  | `ai-review show-config`       |

---

## 💡 Examples

### 🧠 Full Review

Runs the complete review cycle — inline + summary:

```bash
ai-review run
```

### 🧩 Inline Review Only

For quick line-by-line comments:

```bash
ai-review run-inline
```

Typical in CI/CD pipelines for fast feedback on changed files.

### 🧠 Context Review

For broader architectural or cross-file feedback:

```bash
ai-review run-context
```

The model receives the entire diff set and can highlight inconsistencies between modules.

### 🗒️ Summary Review

Posts one concise summary comment under the merge/pull request:

```bash
ai-review run-summary
```

Useful when inline feedback isn’t required but a global analysis is.

### 💬 Reply Modes

Generate AI-based follow-ups to existing discussion threads:

```bash
ai-review run-inline-reply
ai-review run-summary-reply
```

Replies only to comments originally created by AI Review.

### 🧽 Clear Inline Comments

Removes all AI-generated inline comments:

```bash
ai-review clear-inline
```

### 🧽 Clear Summary Comments

Removes all AI-generated summary comments:

```bash
ai-review clear-summary
```

### ⚙️ Inspect Configuration

Display the resolved configuration used by the CLI:

```bash
ai-review show-config
```

Output (formatted JSON):

```json
{
  "llm": {
    "provider": "OPENAI",
    "meta": {
      "model": "gpt-4o-mini",
      "temperature": 0.3
    }
  },
  "vcs": {
    "provider": "GITLAB",
    "pipeline": {
      "project_id": 1
    }
  }
}
```

---

## ⚙️ Tips

- Each command runs **asynchronously** and handles exceptions internally.
- All reviews report **token usage** and **LLM cost** after completion.
- The CLI is designed for **non-interactive** use — perfect for CI/CD jobs.