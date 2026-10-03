# 📘 AI Review Hooks

AI Review provides a **lightweight asynchronous hooks system** that lets you subscribe to internal lifecycle events.

Hooks allow you to:

- log important steps (start, complete, error),
- collect metrics and cost reports,
- trigger external integrations or notifications.

All hooks run **asynchronously** and are **non-blocking** — exceptions are caught and logged without interrupting the
review.

---

## 📑 Table of Contents

- [🧠 Lifecycle](#-lifecycle)
- [🔧 Registration](#-registration)
- [📘 Hook Reference](#-hook-reference)
    - [💬 Chat](#-chat)
    - [🧩 Inline Review](#-inline-review)
    - [🧠 Context Review](#-context-review)
    - [📄 Summary Review](#-summary-review)
    - [🧩 Inline Reply Review](#-inline-reply-review)
    - [🧠 Summary Reply Review](#-summary-reply-review)
    - [💬 Inline Comments](#-inline-comments)
    - [🗒️ Summary Comments](#-summary-comments)
    - [💬 Inline Comment Replies](#-inline-comment-replies)
    - [🗒️ Summary Comment Replies](#-summary-comment-replies)
- [📊 Example: metrics collection](#-example-metrics-collection)
- [⚠️ Error Handling](#-error-handling)

---

## 🧠 Lifecycle

AI Review triggers hooks at key points in the review pipeline:

| Stage                   | Hooks                                                                                                   |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| Chat (LLM call)         | `ON_CHAT_START`, `ON_CHAT_ERROR`, `ON_CHAT_COMPLETE`                                                    |
| Inline Review           | `ON_INLINE_REVIEW_START`, `ON_INLINE_REVIEW_COMPLETE`                                                   |
| Context Review          | `ON_CONTEXT_REVIEW_START`, `ON_CONTEXT_REVIEW_COMPLETE`                                                 |
| Summary Review          | `ON_SUMMARY_REVIEW_START`, `ON_SUMMARY_REVIEW_COMPLETE`                                                 |
| Inline Reply Review     | `ON_INLINE_REPLY_REVIEW_START`, `ON_INLINE_REPLY_REVIEW_COMPLETE`                                       |
| Summary Reply Review    | `ON_SUMMARY_REPLY_REVIEW_START`, `ON_SUMMARY_REPLY_REVIEW_COMPLETE`                                     |
| Inline Comments         | `ON_INLINE_COMMENT_START`, `ON_INLINE_COMMENT_ERROR`, `ON_INLINE_COMMENT_COMPLETE`                      |
| Summary Comments        | `ON_SUMMARY_COMMENT_START`, `ON_SUMMARY_COMMENT_ERROR`, `ON_SUMMARY_COMMENT_COMPLETE`                   |
| Inline Comment Replies  | `ON_INLINE_COMMENT_REPLY_START`, `ON_INLINE_COMMENT_REPLY_ERROR`, `ON_INLINE_COMMENT_REPLY_COMPLETE`    |
| Summary Comment Replies | `ON_SUMMARY_COMMENT_REPLY_START`, `ON_SUMMARY_COMMENT_REPLY_ERROR`, `ON_SUMMARY_COMMENT_REPLY_COMPLETE` |

---

## 🔧 Registration

Hooks are registered via decorators from the global hook instance:

```python
# ./hooks.py
from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.hook import hook
from ai_review.services.review.internal.inline.schema import InlineCommentSchema


@hook.on_chat_start
async def log_chat_start(prompt: str, prompt_system: str):
    print(f"Chat started (length={len(prompt)} chars)")


@hook.on_chat_complete
async def log_chat_complete(result: str, report: CostReportSchema | None):
    if report:
        print(f"Tokens used: {report.completion_tokens}")


@hook.on_inline_comment_complete
async def log_comment(comment: InlineCommentSchema):
    print(f"Comment posted on {comment.file}:{comment.line}")

```

> ⚙️ Each function must be async (`async def`). If a hook raises an error, it is logged but does not affect the main
> review flow.

---

## 📘 Hook Reference

### 💬 Chat

| Hook               | Args                                              | Description                        |
|--------------------|---------------------------------------------------|------------------------------------|
| `on_chat_start`    | `(prompt: str, prompt_system: str)`               | Before sending a prompt to the LLM |
| `on_chat_error`    | `(prompt: str, prompt_system: str)`               | When an LLM request fails          |
| `on_chat_complete` | `(result: str, report: CostReportSchema \| None)` | After LLM response is received     |

### 🧩 Inline Review

| Hook                        | Args                                 |
|-----------------------------|--------------------------------------|
| `on_inline_review_start`    | `()`                                 |
| `on_inline_review_complete` | `(report: CostReportSchema \| None)` |

### 🧠 Context Review

| Hook                         | Args                                 |
|------------------------------|--------------------------------------|
| `on_context_review_start`    | `()`                                 |
| `on_context_review_complete` | `(report: CostReportSchema \| None)` |

### 📄 Summary Review

| Hook                         | Args                                 |
|------------------------------|--------------------------------------|
| `on_summary_review_start`    | `()`                                 |
| `on_summary_review_complete` | `(report: CostReportSchema \| None)` |

### 🧩 Inline Reply Review

| Hook                              | Args                                 | Description                          |
|-----------------------------------|--------------------------------------|--------------------------------------|
| `on_inline_reply_review_start`    | `()`                                 | Before starting inline reply review  |
| `on_inline_reply_review_complete` | `(report: CostReportSchema \| None)` | After completing inline reply review |

### 🧠 Summary Reply Review

| Hook                               | Args                                 | Description                           |
|------------------------------------|--------------------------------------|---------------------------------------|
| `on_summary_reply_review_start`    | `()`                                 | Before starting summary reply review  |
| `on_summary_reply_review_complete` | `(report: CostReportSchema \| None)` | After completing summary reply review |

### 💬 Inline Comments

| Hook                         | Args                             |
|------------------------------|----------------------------------|
| `on_inline_comment_start`    | `(comment: InlineCommentSchema)` |
| `on_inline_comment_error`    | `(comment: InlineCommentSchema)` |
| `on_inline_comment_complete` | `(comment: InlineCommentSchema)` |

### 🗒️ Summary Comments

| Hook                          | Args                              |
|-------------------------------|-----------------------------------|
| `on_summary_comment_start`    | `(comment: SummaryCommentSchema)` |
| `on_summary_comment_error`    | `(comment: SummaryCommentSchema)` |
| `on_summary_comment_complete` | `(comment: SummaryCommentSchema)` |

### 💬 Inline Comment Replies

| Hook                               | Args                                | Description                   |
|------------------------------------|-------------------------------------|-------------------------------|
| `on_inline_comment_reply_start`    | `(reply: InlineCommentReplySchema)` | Before creating inline reply  |
| `on_inline_comment_reply_error`    | `(reply: InlineCommentReplySchema)` | When inline reply fails       |
| `on_inline_comment_reply_complete` | `(reply: InlineCommentReplySchema)` | After publishing inline reply |

### 🗒️ Summary Comment Replies

| Hook                                | Args                                 | Description                    |
|-------------------------------------|--------------------------------------|--------------------------------|
| `on_summary_comment_reply_start`    | `(reply: SummaryCommentReplySchema)` | Before creating summary reply  |
| `on_summary_comment_reply_error`    | `(reply: SummaryCommentReplySchema)` | When summary reply fails       |
| `on_summary_comment_reply_complete` | `(reply: SummaryCommentReplySchema)` | After publishing summary reply |

---

## 📊 Example: metrics collection

You can collect timing and cost information using chat hooks:

```python
import time

from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.hook import hook


@hook.on_chat_start
async def start_timer(prompt: str, prompt_system: str):
    global _start
    _start = time.time()


@hook.on_chat_complete
async def log_duration(result: str, report: CostReportSchema | None):
    elapsed = time.time() - _start
    cost = report.total_cost if report else "n/a"
    print(f"LLM call finished in {elapsed:.2f}s — cost: {cost}")

```

---

## ⚠️ Error Handling

If a callback raises an exception, AI Review logs it safely:

```text
Error in ON_INLINE_COMMENT_COMPLETE hook: ValueError('...')
```

Execution continues normally. This ensures hooks remain safe even in CI/CD pipelines.

---

✅ Hooks are ideal for logging, analytics, and CI/CD integrations. They provide a safe, async, and extensible way to
react to internal events during review.
