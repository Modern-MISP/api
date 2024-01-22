from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from mmisp.db.database import get_db
from mmisp.api_schemas.users.users_view_me_response import UsersViewMeResponse
from ..auth import authorize, AuthStrategy, Auth

router = APIRouter(tags=["users"])


@router.get("/users/view/me")
async def get_logged_in_user_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> UsersViewMeResponse:
    # assemble UsersViewMeResponse through database and IDs in auth object
    return UsersViewMeResponse()
