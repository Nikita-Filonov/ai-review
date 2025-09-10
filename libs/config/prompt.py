import yaml
from pydantic import BaseModel, FilePath


class PromptMetaConfig(BaseModel):
    model: str = "gpt-4o-mini"
    language: str
    category: str
    max_tokens: int = 1200
    temperature: float = 0.3
    description: str | None = None


class PromptConfig(BaseModel):
    meta_prompt_file: FilePath
    inline_prompt_file: FilePath
    summary_prompt_file: FilePath

    def load_meta(self) -> PromptMetaConfig:
        data = yaml.safe_load(self.meta_prompt_file.read_text(encoding="utf-8"))
        return PromptMetaConfig(**data)

    def load_inline(self) -> str:
        return self.inline_prompt_file.read_text(encoding="utf-8")

    def load_summary(self) -> str:
        return self.summary_prompt_file.read_text(encoding="utf-8")
