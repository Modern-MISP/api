from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.future import select

from mmisp.api_schemas.roles import RoleAttributeResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.role import Role

router = APIRouter(tags=["roles"])


@router.get(
    "/roles",
    summary="Get all roles",
)
async def get_all_roles(
    db: Annotated[Session, Depends(get_db)],
) -> list[RoleAttributeResponse]:
    """
    Get all roles and their details.

    Input:

    - Authentification details of the logged in user.

    Output:

    - Information about all roles.
    """
    return await _get_roles(db)


# --- endpoint logic ---


async def _get_roles(db: Session) -> list[RoleAttributeResponse]:
    query = select(Role)

    result = await db.execute(query)
    roles = result.scalars().all()
    role_list: list[RoleAttributeResponse] = []

    for role in roles:
        role_list.append(RoleAttributeResponse(**role.__dict__))
    return role_list
