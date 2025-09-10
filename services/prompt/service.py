from config import settings


class PromptService:
    @classmethod
    def build_inline_request(cls, diff: str) -> str:
        inline = settings.prompt.load_inline()
        return f"{inline}\n\n# Diff\n{diff}"
    
    @classmethod
    def build_summary_request(cls, diffs: list[str]) -> str:
        changes = "\n\n".join(diffs)
        summary = settings.prompt.load_summary()
        return f"{summary}\n\n# Changes\n{changes}"
