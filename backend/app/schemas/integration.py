from pydantic import BaseModel


class OAuthURLRequest(BaseModel):
    provider: str


class OAuthCodeExchangeRequest(BaseModel):
    provider: str
    code: str
    state: str | None = None
