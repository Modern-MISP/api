from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from mmisp.api_schemas.users.users_view_me_response import UsersViewMeResponse
from mmisp.db.database import get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.user import User

from ..auth import Auth, AuthStrategy, authorize

router = APIRouter(tags=["users"])


@router.get("/users/view/me")
async def get_logged_in_user_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> UsersViewMeResponse:
    user = db.get(User, auth.user_id)
    organisation = db.get(Organisation, auth.org_id)
    role = db.get(Role, auth.role_id)

    return UsersViewMeResponse(User=user, Organisation=organisation, Role=role)
