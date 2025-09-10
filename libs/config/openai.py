from pydantic import BaseModel, HttpUrl


class OpenAIHTTPClientConfig(BaseModel):
    api_url: HttpUrl
    api_token: str
