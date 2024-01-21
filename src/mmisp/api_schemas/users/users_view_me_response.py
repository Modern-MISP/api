from pydantic import BaseModel

from ..organisations.organisation import Organisation
from ..roles.role import Role
from .user import User


class UsersViewMeResponse(BaseModel):
    User: User
    Role: Role
    UserSetting: list = []
    Organisation: Organisation
