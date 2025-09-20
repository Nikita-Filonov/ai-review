from enum import StrEnum

from pydantic import BaseModel


class LoggerLevel(StrEnum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerConfig(BaseModel):
    level: LoggerLevel = LoggerLevel.INFO
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[logger_name]} | {message}"
