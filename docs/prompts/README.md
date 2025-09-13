# Prompt Examples

This folder contains **ready-to-use prompt templates** for AI Review.  
They extend the built-in global prompts (`prompts/global_inline.md`, `prompts/global_summary.md`) and define **style &
tone** of the review.

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

In your `.ai-review.yaml`, point to the desired inline & summary prompts:

```yaml
prompt:
  inline_prompt_file: ./docs/prompts/inline_python_light.md
  summary_prompt_file: ./docs/prompts/summary_python_light.md
```

or, for a stricter Go review:

```yaml
prompt:
  inline_prompt_file: ./docs/prompts/inline_go_strict.md
  summary_prompt_file: ./docs/prompts/summary_go_strict.md
```

## 📝 Notes

- Global prompts always enforce JSON/plain-text formats → you don’t need to repeat schema rules.
- These examples are starting points: copy & tweak them for your project’s style guide.
- You can mix & match (e.g., `inline_go_strict.md` with `summary_go_light.md`).