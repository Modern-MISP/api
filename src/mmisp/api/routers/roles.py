from typing import Annotated

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.roles import (
    GetRolesResponse,
    GetRoleResponse,
    RoleAttributeResponse,
    AddRoleResponse,
    DeleteRoleResponse,
    EditRoleResponse
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.role import Role
from mmisp.lib.logger import alog
from fastapi import Path
from mmisp.lib.permissions import Permission

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

    args:

    - Authentification details of the logged in user.

    returns:

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

    args:

    - Authentification details of the logged in user.

    - The current database

    - The role ID

    returns:

    - Information about the roles.
    """
    return await None


@router.post(
    "/admin/roles/add",
    status_code=status.HTTP_200_OK,
    summary="Add new role",
)
async def add_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: AddRoleBody,
) -> AddRoleResponse:
    """Add a new role with the given details.

    args:

    - the user's authentification status

    - the current database

    - the request body containing the new role and its requested permissions

    returns:

    - the new role
    """
    return None


@router.delete(
    "/admin/roles/delete/{roleId}",
    status_code=status.HTTP_200_OK,
    summary="Delete a role",
)
async def delete_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[int, Path(alias="roleId")],
) -> DeleteRoleResponse:
    """Delete a role specified by its role ID. 

    args:

    - the user's authentification status

    - the current database

    - the role ID

    returns:

    - the deleted role
    """
    return await None


@router.put(
    "/admin/roles/edit/{roleId}",
    status_code=status.HTTP_200_OK,
    summary="Edit a role",
)
async def update_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[str, Path(alias="roleId")],
    body: EditRoleBody,
) -> EditRoleResponse:
    """Update an existing event either by its event ID or via its UUID. 

    args:

    - the user's authentification status

    - the current database

    - the ID of the role

    - the request body

    returns:

    - the updated event
    """
    return await None


@router.post(
    "/roles/reinstate",
    status_code=status.HTTP_200_OK,
    summary="Reinstate a deleted standard role",
)
async def reinstate_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[str, Path(alias="roleId")],
    body: ReinstateRoleBody,
) -> ReinstateRoleResponse:
    """Reinstate a deleted standard role.

    args:

    - the user's authentication status
    - the current database
    - the role id
    - the requested body containing the name of the requested standard role

    returns:

    - the updated role

    raises:

    - 200: Successful Response
    - 422: Validation Error
    - 403: Forbidden Error
    - 404: Not Found Error
    """
    return await _reinstate_role(auth, db, role_id, body)


@router.post(
    "/roles/restSearch",
    status_code=status.HTTP_200_OK,
    summary="Search roles with filters",
)
async def filter_roles(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: FilterRoleBody,
) -> list[FilterRoleResponse]:
    """Search roles based on filters.

    Input:

    - the user's authentication status
    - the current database
    - the requested body containing the requested filter data

    Output:

    - the searched and filtered roles

    Responses:

    - 200: Successful Response
    - 422: Validation Error
    - 403: Forbidden Error
    - 404: Not Found Error
    """
    return await _filter_roles(auth, db, body)


@router.put(
    "/admin/users/edit/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Assign or reassign a user to a specific role",
)
async def edit_user_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ADMIN, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
    body: EditUserRoleBody,
) -> EditUserRoleResponse:
    """Assign or reassign a user to a specific role.

    Input:

    - authentication details
    - database session
    - user_id: ID of the user for whom the setting is to be updated
    - body: new role for updating the user setting

    Output:

    - the updated user

    Responses:

    - 200: Successful Response
    - 422: Validation Error
    - 403: Forbidden Error
    - 404: Not Found Error
    """
    return await _edit_user_role(auth, db, user_id, body)


@router.put(
    "/admin/roles/setDefault",
    status_code=status.HTTP_200_OK,
    summary="Change the default role",
)
async def set_default_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ADMIN, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: DefaultRoleBody,
) -> DefaultRoleResponse:
    """Change the default role (if not changed the default role is 'read only').

    Input:

    - the user's authentication status
    - the current database
    - the requested body containing the new default role

    Output:

    - the new default role

    Responses:

    - 200: Successful Response
    - 422: Validation Error
    - 403: Forbidden Error
    - 404: Not Found Error

    """
    return await _set_default_role(auth, db, body)


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
