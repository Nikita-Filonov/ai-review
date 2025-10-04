from pydantic import BaseModel, HttpUrl, SecretStr


class HTTPClientConfig(BaseModel):
    timeout: float = 120
    api_url: HttpUrl

    @property
    def api_url_value(self) -> str:
        return str(self.api_url)


class HTTPClientWithTokenConfig(HTTPClientConfig):
    api_token: SecretStr

    @property
    def api_token_value(self) -> str:
        return self.api_token.get_secret_value()
