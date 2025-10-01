from pydantic import BaseModel


class CoreConfig(BaseModel):
    concurrency: int = 7
