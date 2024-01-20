from pydantic import BaseModel
from enum import Enum


class LoginType(Enum):
    PASSWORD = "password"
    IDENTITY_PROVIDER = "idp"


class IdentityProviderInfo(BaseModel):
    id: str
    name: str


class StartLoginResponse(BaseModel):
    loginType: LoginType
    identityProviders: list[IdentityProviderInfo] = []
