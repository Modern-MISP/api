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


@router.get(
    "/roles/{roleId}",
    summary="Get role details",
)
async def get_role_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[int, Path(alias="roleId")],
) -> GetRoleResponse:
    """
    Gets the details of the specified role.

    Input:

    - Authentification details of the logged in user.

    - The current database

    - The role Id

    Output:

    - Information about the roles.
    """
    return await None


@router.post(
    "/roles",
    status_code=status.HTTP_200_OK,
    response_model=AddRoleResponse,
    summary="Add new role",
)
async def add_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    body: AddRoleBody,
) -> AddRoleResponse:
    """Add a new role with the given details.

    Input:

    - the user's authentification status

    - the current database

    - the request body containing the new role and its requested permissions

    Output:

    - the new role
    """
    return None


@router.delete(
    "/roles/{roleId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteRoleResponse,
    summary="Delete a role",
)
async def delete_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[int, Path(alias="roleId")],
) -> DeleteRoleResponse:
    """Delete a role specified by its role Id. 
    # FIXME Permissions missing

    Input:

    - the user's authentification status

    - the current database

    - the role Id

    Output:

    - the deleted role
    """
    return await None



@router.put(
    "/roles/edit/{roleId}",
    status_code=status.HTTP_200_OK,
    response_model=EditRoleResponse,
    summary="Edit a role",
)
async def update_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[str, Path(alias="roleId")],
    body: EditRoleBody,
) -> EditRoleResponse:
    """Update an existing event either by its event id or via its UUID. 

    Input:

    - the user's authentification status

    - the current database

    - the id of the role

    - the request body

    Output:

    - the updated event
    """
    return await None





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
