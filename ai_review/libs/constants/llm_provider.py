from enum import StrEnum


class LLMProvider(StrEnum):
    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    CLAUDE = "CLAUDE"
