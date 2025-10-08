from pydantic import BaseModel


class BitbucketUserSchema(BaseModel):
    uuid: str
    nickname: str
    display_name: str
