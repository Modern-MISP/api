from enum import Enum

from pydantic import BaseModel


class LoginType(Enum):
    PASSWORD = "password"
    IDENTITY_PROVIDER = "idp"


class IdentityProviderInfo(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


class StartLoginResponse(BaseModel):
    loginType: LoginType
    identityProviders: list[IdentityProviderInfo] = []
