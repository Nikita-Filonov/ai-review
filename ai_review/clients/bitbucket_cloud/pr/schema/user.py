from pydantic import BaseModel


class BitbucketCloudUserSchema(BaseModel):
    uuid: str | None = None
    nickname: str | None = None
    display_name: str | None = None
