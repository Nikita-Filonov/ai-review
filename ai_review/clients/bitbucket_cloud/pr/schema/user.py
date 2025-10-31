from pydantic import BaseModel


class BitbucketCloudUserSchema(BaseModel):
    uuid: str
    nickname: str
    display_name: str
