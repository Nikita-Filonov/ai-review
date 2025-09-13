Return ONLY a valid JSON array of inline review comments.

Format:

```json
[
  {
    "file": "<relative_file_path>",
    "line": <line_number>,
    "message": "<short review message>"
  }
]
```

Rules:

- "file" must exactly match the file path in the diff.
- "line" must be an integer from the new version of the file.
- "message" must be a short, actionable review comment.
- Do not include anything outside the JSON array.
- If no issues are found, return [].