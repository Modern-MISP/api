from pydantic import BaseModel


class UserOrgId(BaseModel):
    id: str = ""
    org_id: str = ""


class AuthKeyEditSchema(BaseModel):
    id: int = ""
    uuid: str = ""
    authkey_start: str = ""
    authkey_end: str = ""
    created: str = ""
    expiration: str = ""
    read_only: bool = False
    user_id: str = ""
    comment: str = ""
    allowed_ips: list[str] = {""}
    user: UserOrgId = UserOrgId()
