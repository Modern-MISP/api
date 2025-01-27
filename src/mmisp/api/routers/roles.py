from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.future import select, exists

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.roles import (
    GetRolesResponse,
    GetRoleResponse,
    RoleAttributeResponse,
    AddRoleBody,
    AddRoleResponse,
    DeleteRoleResponse,
    EditRoleBody,
    EditRoleResponse,
    ReinstateRoleBody,
    ReinstateRoleResponse,
    FilterRoleBody,
    FilterRoleResponse,
    EditUserRoleBody,
    EditUserRoleResponse,
    GetUserRoleResponse,
    DefaultRoleResponse)

from mmisp.db.database import Session, get_db
from mmisp.db.models.role import Role
from mmisp.lib.logger import alog
from fastapi import Path
from mmisp.lib.permissions import Permission
from mmisp.db.models.user import User

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
        auth: the user's authentification status

    returns:
        information about all roles
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
        auth: the user's authentification status
        db: the current database
        role_id: the role ID

    returns:
        information about the role
    """

    return await _get_role(db, role_id)


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
        auth: the user's authentification status
        db: the current database
        body: the request body containing the new role and its requested permissions

    returns:
        the new role
    """
    return _add_role(db, AddRoleBody)


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
        auth: the user's authentification status
        db: the current database
        role_id: the ID of the role

    returns:
        the deleted role
    """
    return await _delete_role(db, role_id)


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
        auth: the user's authentification status
        db: the current database
        role_id: the ID of the role
        body: the request body

    returns:
        the updated event
    """
    return None


@router.post(
    "/roles/reinstate",
    status_code=status.HTTP_200_OK,
    summary="Reinstate a deleted standard role",
)
async def reinstate_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[str, Path(alias="roleId")],
) -> ReinstateRoleResponse:
    """Reinstate a deleted standard role.

    args:
        auth: the user's authentication status
        db: the current database
        role_id: the role id of the to be reinstated role

    returns:
        the reinstated role

    raises:
        200: Successful Response
        422: Validation Error
        403: Forbidden Error
        404: Not Found Error
    """
    return await None # _reinstate_role(auth, db, role_id)


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

    args:
        auth: the user's authentication status
        db: the current database
        body: the requested body containing the requested filter data

    returns:
        the searched and filtered roles

    raises:
        200: Successful Response
        422: Validation Error
        403: Forbidden Error
        404: Not Found Error
    """
    return await _filter_roles(auth, db, body)


@router.put(
    "/admin/users/edit/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Assign or reassign a user to a specific role",
)
async def edit_user_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
    body: EditUserRoleBody,
) -> EditUserRoleResponse:
    """Assign or reassign a user to a specific role.

    args:
        auth: authentication details
        db: database session
        user_id: ID of the user for whom the setting is to be updated
        body: new role for updating the users roles

    returns:
        the updated user

    raises:
        200: Successful Response
        422: Validation Error
        403: Forbidden Error
        404: Not Found Error
    """
    return None


@router.post(
    "admin/roles/users/{roleId}",
    status_code=status.HTTP_200_OK,
    summary="Get all users assigned to a specific role",
)
async def get_users_by_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[int, Path(alias="roleId")],
) -> list[GetUserRoleResponse]:
    """
    Retrieve all users assigned to a specific role.

    Args:
        auth: the user's authentication details.
        db: the current database session.
        role_id: the ID of the role whose users are requested.

    Returns:
        A list of users assigned to the specified role.

    Raises:
        200: Successful Response.
        422: Validation Error.
        403: Forbidden Error.
        404: Not Found Error.
    """
    return await _get_users_by_role(auth, db, role_id)


@router.put(
    "/admin/roles/setDefault/{roleId}",
    status_code=status.HTTP_200_OK,
    summary="Change the default role",
)
async def set_default_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[int, Path(alias="roleId")],
) -> DefaultRoleResponse:
    """Change the default role (if not changed the default role is 'read only').

    args:
        auth: the user's authentication status
        db: the current database
        body: the requested body containing the new default role

    returns:
        the new default role

    raises:
        200: Successful Response
        422: Validation Error
        403: Forbidden Error
        404: Not Found Error

    """
    return await _set_default_role(auth, db, role_id)


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



async def _get_role(db: Session, role_id: int) -> GetRoleResponse:
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=GetRoleResponse(
                saved=False,
                name="Role not found",
                message=f"Role with ID {role_id} not found.",
                url=f"/roles/{role_id}",
                id=role_id,
            ).dict(),
        )

    return GetRoleResponse(Role=RoleAttributeResponse(**role.__dict__))



async def _delete_role(db: Session, role_id: int) -> DeleteRoleResponse:
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteRoleResponse(
                saved=False,
                name="Role not found",
                message=f"Role with ID {role_id} not found.",
                url=f"/admin/roles/delete/{role_id}",
                id=role_id,
            ).dict(),
        )

    if role.default_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteRoleResponse(
                saved=False,
                name="Can't delete default role",
                message=f"Role with ID {role_id} is the default role. Can't be deleted",
                url=f"/admin/roles/delete/{role_id}",
                id=role_id,
            ).dict(),
        )
    
    user_exists = await db.execute(select(exists().where(User.role_id == role_id)))

    if user_exists.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DeleteRoleResponse(
                saved=False,
                name="Role in use",
                message=f"Role with ID {role_id} cannot be deleted because it is assigned to one or more users.",
                url=f"/admin/roles/delete/{role_id}",
                id=role_id,
            ).dict(),
        )

    await db.delete(role)
    await db.commit()

    return DeleteRoleResponse(
        Role=RoleAttributeResponse(**role.__dict__),
        saved=True,
        success=True,
        name="Role deleted",
        message="Role deleted",
        url=f"/admin/roles/delete/{role_id}",
        id=str(role_id),
    )


async def _reinstate_role(auth: Auth, db: Session, role_id: int) -> ReinstateRoleResponse:
    # Standard roles must have an ID between 1 and 7 since those are the only ones that are always available 
    if role_id < 1 or role_id > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with ID {role_id} is not a standard role and cannot be reinstated."
        )

    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with ID {role_id} is already in use."
        )

    # FIXME REINSTATE ROLE WITH THE PASSED ON ID HERE

    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    return ReinstateRoleResponse(
        Role=RoleAttributeResponse(**role.__dict__),
        success=True,
        message=f"Role with ID {role_id} has been reinstated.",
        url=f"/roles/reinstate/{role_id}",
        id=role_id
    )


async def _filter_roles(auth: Auth, db: Session, body: FilterRoleBody) -> list[FilterRoleResponse]:
    requested_permissions = body.permissions

    if not requested_permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No permissions provided for filtering."
        )

    query = select(Role)
    result = await db.execute(query)
    roles = result.scalars().all()

    filtered_roles: list[FilterRoleResponse] = []

    for role in roles:
        role_permissions = role.get_permissions()

        if all(permission in role_permissions for permission in requested_permissions):
            filtered_roles.append(FilterRoleResponse(Role=RoleAttributeResponse(**role.__dict__)))

    return filtered_roles



async def _edit_user_role(auth: Auth, db: Session, user_id: str, body: EditUserRoleBody) -> EditUserRoleResponse:

    if not body.role_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="value 'role_id' is required")
    if not isinstance(body.role_id, int):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN_BAD_REQUEST, detail="invalid 'role_id'")

    user = await db.get(User, auth.user_id)
    if user is None:
        # this should never happen, it would mean, the user disappeared between auth and processing the request
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user not available")

    result = await db.execute(select(Role).where(Role.id == body.role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EditUserRoleResponse(
                saved=False,
                name="Role not found",
                message=f"Role with ID {body.role_id} not found.",
                url=f"/admin/roles/delete/{body.role_id}",
                id=body.role_id,
            ).dict(),
        )

    user.role_id = body.role_id  
    await db.commit()

    return EditUserRoleResponse(
        saved=True,
        success=True,
        name="User role updated",
        message=f"User's role has been updated to {role.name}.",
        url=f"/admin/users/edit/{user_id}",
        id=user.id,
        Role=role.name,  
    )



async def _get_users_by_role(auth: Auth, db: Session, role_id: int) -> list[GetUserRoleResponse]:
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found."
        )

    users_query = await db.execute(select(User).where(User.role_id == role_id))
    users = users_query.scalars().all()

    if not users:
        return []

    user_list: list[GetUserRoleResponse] = [GetUserRoleResponse(user=user) for user in users]

    return user_list



async def _set_default_role(auth: Auth, db: Session, role_id: int) -> DefaultRoleResponse:
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DefaultRoleResponse(
                saved=False,
                name="Role not found",
                message=f"Role with ID {role_id} not found.",
                url=f"/admin/roles/delete/{role_id}",
                id=role_id,
            ).dict(),
        )
    
    current_default_role = await db.execute(select(Role).where(Role.default_role == True))
    current_default_role = current_default_role.scalar_one_or_none()

    # there should always be a default role, since the default role can't be deleted, but just in case...
    if current_default_role:
        current_default_role.default_role = False
        await db.commit()

    role.default_role = True
    await db.commit()

    return DefaultRoleResponse(
        Role=RoleAttributeResponse(**role.__dict__),
        saved=True,
        success=True,
        name="Default Role Changed",
        message=f"The default role has been changed to {role.name}.",
        url="/admin/roles/setDefault/{role_id}",
        id=role_id,
    )
