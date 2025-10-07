Return ONLY a valid JSON object representing a single inline comment reply.

Format:

```json
{
  "message": "<short reply message to the comment thread>",
  "suggestion": "<replacement code block without markdown, or null if not applicable>"
}
```

Rules:

- Output must be a single JSON object, not an array.
- "message" — required, non-empty, plain text.
    - Keep it short and focused (1–2 sentences).
    - Do not repeat or quote previous comments.
    - Respond only within the scope of the given thread.
- "suggestion" — optional.
    - If you propose a code change, provide only the replacement code (no markdown, no comments).
    - Use correct indentation and consistent style with the diff.
    - If no code change is appropriate, set "suggestion" to null.
- Never include any additional fields or text outside the JSON object.
- If no meaningful reply is needed, return:

```json
{
  "message": "No reply.",
  "suggestion": null
}
```