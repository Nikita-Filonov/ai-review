def truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text

    omitted = len(text) - limit
    return f"{text[:limit]}\n\n... output truncated ({omitted} chars omitted)"
