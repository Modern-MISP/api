from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.roles import (
    AddRoleBody,
    AddRoleResponse,
    DefaultRoleResponse,
    DeleteRoleResponse,
    EditRoleBody,
    EditRoleResponse,
    FilterRoleBody,
    FilterRoleResponse,
    GetRoleResponse,
    GetRolesResponse,
    GetUserRoleResponse,
    IndexRole,
    IndexRolesResponse,
    ReinstateRoleResponse,
    RoleAttributeResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.role import Role
from mmisp.db.models.user import User
from mmisp.lib.logger import alog
from mmisp.lib.permissions import Permission
from mmisp.lib.settings import get_admin_setting
from mmisp.lib.standard_roles import get_standard_roles

router = APIRouter(tags=["roles"])


@router.get(
    "/roles/index",
    summary="Get all roles",
)
@router.get(
    "/roles",
    summary="Get all roles",
)
@alog
async def get_all_roles(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[IndexRolesResponse]:
    """
    Get all roles and their details.

    args:
        auth: the user's authentification status

    returns:
        information about all roles
    """
    return await _get_roles_index(db)


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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
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
    return await _add_role(db, body)


@router.delete(
    "/admin/roles/delete/{roleId}",
    status_code=status.HTTP_200_OK,
    summary="Delete a role",
)
async def delete_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[int, Path(alias="roleId")],
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
    return await _update_role(db, role_id, body)


@router.post(
    "/roles/reinstate/{roleId}",
    status_code=status.HTTP_200_OK,
    summary="Reinstate a deleted standard role",
)
async def reinstate_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    role_id: Annotated[int, Path(alias="roleId")],
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
    return await _reinstate_role(auth, db, role_id)


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


@router.post(
    "/admin/roles/users/{roleId}",
    status_code=status.HTTP_200_OK,
    summary="Get all users assigned to a specific role",
)
async def get_users_by_role(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
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


# --- deprecated ---

# --- endpoint logic ---


@alog
async def _get_roles(db: Session) -> list[GetRolesResponse]:
    query = select(Role)

    result = await db.execute(query)
    roles = result.scalars().all()
    role_list: list[GetRolesResponse] = []

    for role in roles:
        role_list.append(GetRolesResponse(Role=RoleAttributeResponse(**role.asdict())))
    return role_list


@alog
async def _get_roles_index(db: Session) -> list[IndexRolesResponse]:
    db_entry = await get_admin_setting(db, "default_role")
    if db_entry is not None:
        try:
            default_role_id = int(db_entry)
        except ValueError:
            default_role_id = None
    else:
        default_role_id = None

    query = select(Role)

    result = await db.execute(query)
    roles = result.scalars().all()

    return [IndexRolesResponse(Role=IndexRole(**role.asdict(), default=(role.id == default_role_id))) for role in roles]


async def _get_role(db: Session, role_id: int) -> GetRoleResponse:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {role_id} not found.")

    return GetRoleResponse(Role=RoleAttributeResponse(**role.asdict()))


async def _add_role(db: Session, body: AddRoleBody) -> AddRoleResponse:
    if body is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body cannot be None.")

    max_id_result = await db.execute(select(Role.id).order_by(Role.id.desc()).limit(1))
    max_id = max_id_result.scalar_one_or_none()
    # ID 1-6 is reserved for the predefined standard roles
    role_id = max(7, (max_id + 1) if max_id is not None else 7)

    role = Role(
        id=role_id,
        name=body.name,
        created=datetime.now(timezone.utc),
        perm_add=body.perm_add,
        perm_modify=body.perm_modify,
        perm_modify_org=body.perm_modify_org,
        perm_publish=body.perm_publish,
        perm_delegate=body.perm_delegate,
        perm_sync=body.perm_sync,
        perm_admin=body.perm_admin,
        perm_audit=body.perm_audit,
        perm_auth=body.perm_auth,
        perm_site_admin=body.perm_site_admin,
        perm_regexp_access=body.perm_regexp_access,
        perm_tagger=body.perm_tagger,
        perm_template=body.perm_template,
        perm_sharing_group=body.perm_sharing_group,
        perm_tag_editor=body.perm_tag_editor,
        perm_sighting=body.perm_sighting,
        perm_object_template=body.perm_object_template,
        default_role=body.default_role,
        memory_limit=body.memory_limit,
        max_execution_time=body.max_execution_time,
        restricted_to_site_admin=body.restricted_to_site_admin,
        perm_publish_zmq=body.perm_publish_zmq,
        perm_publish_kafka=body.perm_publish_kafka,
        perm_decaying=body.perm_decaying,
        enforce_rate_limit=body.enforce_rate_limit,
        rate_limit_count=body.rate_limit_count,
        perm_galaxy_editor=body.perm_galaxy_editor,
        perm_warninglist=body.perm_warninglist,
        perm_view_feed_correlations=body.perm_view_feed_correlations,
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)

    return AddRoleResponse(
        Role=RoleAttributeResponse(**role.asdict()),
        created=True,
        message=f"Role '{role.name}' successfully created.",
    )


async def _delete_role(db: Session, role_id: int) -> DeleteRoleResponse:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=404,
            detail={"message": "Invalid Role", "name": "Invalid Role", "url": f"/admin/roles/delete/{role_id}"},
        )

    if role.default_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with ID {role_id} is the default role. Can't be deleted",
        )

    result = await db.execute(select(User.id).where(User.role_id == role_id))
    user_exists = result.scalar_one_or_none()

    if user_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with ID {role_id} cannot be deleted because it is assigned to one or more users.",
        )

    await db.delete(role)
    await db.commit()

    return DeleteRoleResponse(
        Role=RoleAttributeResponse(**role.asdict()),
        saved=True,
        success=True,
        name="Role deleted",
        message="Role deleted",
        url=f"/admin/roles/delete/{role_id}",
        id=str(role_id),
    )


async def _update_role(db: Session, role_id: int, body: EditRoleBody) -> EditRoleResponse:
    if body is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body cannot be None.")

    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=404,
            detail={"message": "Invalid Role", "name": "Invalid Role", "url": f"/admin/roles/edit/{role_id}"},
        )

    if all(value is None for value in body.model_dump().values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one new attribute must be provided to update the role.",
        )

    role.patch(**body.model_dump(exclude_unset=True))
    role.modified = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(role)

    return EditRoleResponse(Role=RoleAttributeResponse(**role.asdict()))


async def _reinstate_role(auth: Auth, db: Session, role_id: int) -> ReinstateRoleResponse:
    if role_id < 1 or role_id > 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with ID {role_id} is not a standard role and cannot be reinstated.",
        )

    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role with ID {role_id} is already in use."
        )

    standard_roles = get_standard_roles()
    role = next(role for role in standard_roles if role.id == role_id)

    db.add(role)

    # The reinstated read-only role (id 6) is no longer the default role
    if role_id == 6:
        role.default_role = False

    await db.commit()

    return ReinstateRoleResponse(
        Role=RoleAttributeResponse(**role.asdict()),
        success=True,
        message=f"Role with ID {role_id} has been reinstated.",
        url=f"/roles/reinstate/{role_id}",
        id=role_id,
    )


async def _filter_roles(auth: Auth, db: Session, body: FilterRoleBody) -> list[FilterRoleResponse]:
    if body is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body cannot be None.")

    requested_permissions = body.permissions

    if not requested_permissions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permissions provided for filtering.")

    query = select(Role)
    result = await db.execute(query)
    roles = result.scalars().all()

    filtered_roles: list[FilterRoleResponse] = []

    for role in roles:
        role_permissions = role.get_permissions()

        if all(permission in role_permissions for permission in requested_permissions):
            filtered_roles.append(FilterRoleResponse(Role=RoleAttributeResponse(**role.asdict())))

    return filtered_roles


async def _get_users_by_role(auth: Auth, db: Session, role_id: int) -> list[GetUserRoleResponse]:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {role_id} not found.")

    users_query = await db.execute(select(User).where(User.role_id == role_id))
    users = users_query.scalars().all()

    if not users:
        return []

    user_list: list[GetUserRoleResponse] = [GetUserRoleResponse(user_id=user.id) for user in users]

    return user_list


async def _set_default_role(auth: Auth, db: Session, role_id: int) -> DefaultRoleResponse:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {role_id} not found.")

    if role.default_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role with ID {role_id} is already the default role."
        )

    role_result = await db.execute(select(Role).where(Role.default_role))
    current_default_role = role_result.scalar_one_or_none()

    # there should always be a default role, since the default role can't be deleted, but just in case...
    if current_default_role is not None:
        current_default_role.default_role = False
        await db.commit()

    role.default_role = True
    await db.commit()

    return DefaultRoleResponse(
        Role=RoleAttributeResponse(**role.asdict()),
        saved=True,
        success=True,
        name="Default Role Changed",
        message=f"The default role has been changed to {role.name}.",
        url="/admin/roles/setDefault/{role_id}",
        id=role_id,
    )
