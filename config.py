import os

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource
)

from libs.config.llm import LLMConfig
from libs.config.prompt import PromptConfig
from libs.config.review import ReviewConfig
from libs.config.vcs import VCSConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='allow',

        env_file=os.path.join(os.getcwd(), ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",

        yaml_file=os.path.join(os.getcwd(), ".ai-review.yaml"),
        yaml_file_encoding="utf-8",

        json_file=os.path.join(os.getcwd(), ".ai-review.json"),
        json_file_encoding="utf-8"
    )

    llm: LLMConfig
    vcs: VCSConfig
    prompt: PromptConfig
    review: ReviewConfig

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            YamlConfigSettingsSource(cls),
            JsonConfigSettingsSource(cls),
            env_settings,
            dotenv_settings,
            init_settings,
        )


settings = Settings()
