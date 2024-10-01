from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.roles import (
    GetRolesResponse,
    RoleAttributeResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.role import Role
from mmisp.lib.logger import alog

router = APIRouter(tags=["roles"])


@router.get(
    "/roles",
    summary="Get all roles",
)
@alog
async def get_all_roles(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetRolesResponse]:
    """
    Get all roles and their details.

    Input:

    - Authentification details of the logged in user.

    Output:

    - Information about all roles.
    """
    return await _get_roles(db)


# --- endpoint logic ---


@alog
async def _get_roles(db: Session) -> list[GetRolesResponse]:
    query = select(Role)

    result = await db.execute(query)
    roles = result.scalars().all()
    role_list: list[GetRolesResponse] = []

    for role in roles:
        role_list.append(GetRolesResponse(Role=RoleAttributeResponse(**role.__dict__)))
    return role_list
