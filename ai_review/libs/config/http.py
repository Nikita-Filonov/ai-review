from pydantic import BaseModel, HttpUrl, SecretStr, FilePath


class HTTPClientConfig(BaseModel):
    verify: FilePath | bool | None = True
    timeout: float = 120
    api_url: HttpUrl
    proxy_url: HttpUrl | None = None

    @property
    def api_url_value(self) -> str:
        return str(self.api_url)

    @property
    def proxy_url_value(self) -> str | None:
        return str(self.proxy_url) if self.proxy_url else None


class HTTPClientWithTokenConfig(HTTPClientConfig):
    api_token: SecretStr

    @property
    def api_token_value(self) -> str:
        return self.api_token.get_secret_value()
