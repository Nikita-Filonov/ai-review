import os
from enum import StrEnum


class ConfigEnv(StrEnum):
    ENV = "AI_REVIEW_CONFIG_FILE_ENV"
    YAML = "AI_REVIEW_CONFIG_FILE_YAML"
    JSON = "AI_REVIEW_CONFIG_FILE_JSON"


def get_config_file_or_default(variable: str, default_filename: str) -> str:
    return os.getenv(variable, os.path.join(os.getcwd(), default_filename))


def get_env_config_file_or_default() -> str:
    return get_config_file_or_default(ConfigEnv.ENV, ".env")


def get_yaml_config_file_or_default() -> str:
    return get_config_file_or_default(ConfigEnv.YAML, ".ai-review.yaml")


def get_json_config_file_or_default() -> str:
    return get_config_file_or_default(ConfigEnv.JSON, ".ai-review.json")
