from pydantic import BaseModel, Field, ConfigDict


class BitbucketServerUserSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    name: str
    slug: str | None = None
    type: str | None = None
    active: bool | None = None
    display_name: str = Field(alias="displayName")
    email_address: str | None = Field(default=None, alias="emailAddress")
