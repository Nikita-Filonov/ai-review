from config import settings


class PromptService:
    @classmethod
    def build_inline_request(cls, diff: str) -> str:
        inline = settings.prompt.load_inline()
        global_inline = settings.prompt.load_global_inline()
        return (
            f"{global_inline}\n\n"
            f"{inline}\n\n"
            f"## Diff\n"
            f"```diff\n{diff}\n```\n"
        )

    @classmethod
    def build_summary_request(cls, diffs: list[str]) -> str:
        changes = "\n\n".join(diffs)
        summary = settings.prompt.load_summary()
        global_summary = settings.prompt.load_global_summary()
        return (
            f"{global_summary}\n\n"
            f"{summary}\n\n"
            f"## Changes\n"
            f"```diff\n{changes}\n```"
        )
