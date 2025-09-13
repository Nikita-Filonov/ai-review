from pydantic import BaseModel, FilePath


class PromptConfig(BaseModel):
    inline_prompt_file: FilePath
    summary_prompt_file: FilePath

    global_inline_prompt_file: FilePath = FilePath("./prompts/global_inline.md")
    global_summary_prompt_file: FilePath = FilePath("./prompts/global_summary.md")

    def load_inline(self) -> str:
        return self.inline_prompt_file.read_text(encoding="utf-8")

    def load_summary(self) -> str:
        return self.summary_prompt_file.read_text(encoding="utf-8")

    def load_global_inline(self) -> str:
        return self.global_inline_prompt_file.read_text(encoding="utf-8")

    def load_global_summary(self) -> str:
        return self.global_summary_prompt_file.read_text(encoding="utf-8")
