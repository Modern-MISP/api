from pydantic import BaseModel


class IdentityProviderInfo(BaseModel):
    id: str
    name: str


class StartLoginResponse(BaseModel):
    loginType: str
    identityProviders: list[IdentityProviderInfo]
