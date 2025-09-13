from pydantic import BaseModel, HttpUrl, SecretStr


class HTTPClientConfig(BaseModel):
    timeout: float = 120
    api_url: HttpUrl
    api_token: SecretStr

    @property
    def base_url(self) -> str:
        return str(self.api_url)

    @property
    def bearer_token(self) -> str:
        return self.api_token.get_secret_value()
