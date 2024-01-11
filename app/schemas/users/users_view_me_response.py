from pydantic import BaseModel
from .user import User
from ..roles.role import Role


class UsersViewMeResponse(BaseModel):
    User: User
    Role: Role
    UserSetting: list = []
    Organisation: None  # TODO link organisation schema
