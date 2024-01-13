from pydantic import BaseModel
from .user import User
from ..roles.role import Role
from ..organisations.organisation import Organisation


class UsersViewMeResponse(BaseModel):
    User: User
    Role: Role
    UserSetting: list = []
    Organisation: Organisation
