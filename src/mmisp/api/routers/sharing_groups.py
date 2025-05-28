import uuid
from collections.abc import Sequence
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api.config import config
from mmisp.api_schemas.responses.standard_status_response import StandardStatusResponse
from mmisp.api_schemas.sharing_groups import (
    AddOrgToSharingGroupBody,
    AddOrgToSharingGroupLegacyBody,
    AddServerToSharingGroupBody,
    AddServerToSharingGroupLegacyBody,
    CreateSharingGroupBody,
    CreateSharingGroupLegacyBody,
    CreateSharingGroupLegacyResponse,
    GetSharingGroupsIndex,
    SingleSharingGroupResponse,
    UpdateSharingGroupBody,
    UpdateSharingGroupLegacyBody,
    ViewUpdateSharingGroupLegacyResponse,
)
from mmisp.api_schemas.sharing_groups import SharingGroupOrg as SharingGroupOrgSchema
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.server import Server
from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from mmisp.lib.logger import alog

router = APIRouter(tags=["sharing_groups"])

LOCAL_INSTANCE_SERVER = {"id": 0, "name": "Local instance", "url": config.OWN_URL}


@router.get(
    "/sharing_groups",
    status_code=status.HTTP_200_OK,
    summary="Get all sharing groups",
)
@router.get(
    "/sharing_groups/index",
    status_code=status.HTTP_200_OK,
    summary="Get all sharing groups",
)
@alog
async def get_all_sharing_groups(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
) -> GetSharingGroupsIndex:
    """
    Retrieve a list of all sharing groups.

    Args:
      auth: Authentication details
      db: Database session

    Returns:
      Representation of all sharing groups
    """

    return await _get_all_sharing_groups(auth, db)


@router.post(
    "/sharing_groups",
    status_code=status.HTTP_201_CREATED,
    summary="Add a new sharing group",
)
@alog
async def create_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateSharingGroupBody,
) -> dict:
    """
    Add a new sharing group with given details.

    Args:
      auth: Authentication details
      db: Database session
      body: Request body containing details for creating the sharing group

    Returns:
      Details of the created sharing group
    """
    return await _create_sharing_group(auth, db, body)


@router.get(
    "/sharing_groups/{id}",
    status_code=status.HTTP_200_OK,
    summary="Get sharing group details",
)
@alog
async def get_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int | uuid.UUID,
) -> dict:
    """
    Retrieve details of a specific sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to retrieve

    Returns:
      Representation of the sharing group details
    """
    return await _get_sharing_group(auth, db, id)


@router.put(
    "/sharing_groups/{id}",
    status_code=status.HTTP_200_OK,
    summary="Update sharing group",
)
@alog
async def update_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: UpdateSharingGroupBody,
) -> dict:
    """
    Update an existing sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to update
      body: Request body containing updated details for the sharing group

    Returns:
      Representation of the updated sharing group
    """
    return await _update_sharing_group(auth, db, id, body)


@router.delete(
    "/sharing_groups/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete sharing group",
)
@alog
async def delete_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    """
    Delete a specific sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to delete

    Returns:
      Representation of the deleted sharing group
    """
    return await _delete_sharing_group(auth, db, id)


@router.get(
    "/sharing_groups/{id}/info",
    status_code=status.HTTP_200_OK,
    summary="Additional infos from a sharing group",
)
@alog
async def get_sharing_group_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    """
    Details of a sharing group and org.count, user_count and created_by_email.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to retrieve additional information

    Returns:
      Representation of the sharing group information
    """
    return await _get_sharing_group_info(auth, db, id)


@router.patch(
    "/sharing_groups/{id}/organisations",
    status_code=status.HTTP_200_OK,
)
@alog
async def add_org_to_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: AddOrgToSharingGroupBody,
) -> SharingGroupOrgSchema:
    """
    Add an organisation to a sharing group.

    Args:
      auth: Authentication details
      db: Database session.
      id: ID of the sharing group to add the organisation
      body: Request body containing organisation details

    Returns:
      SharingGroupOrgSchema: Representation of the added organisation in the sharing group
    """
    return await _add_org_to_sharing_group(auth, db, id, body)


@router.delete(
    "/sharing_groups/{id}/organisations/{organisationId}",
    status_code=status.HTTP_200_OK,
    summary="Remove an organisation",
)
@alog
async def remove_org_from_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    organisation_id: Annotated[int, Path(alias="organisationId")],
) -> dict:
    """
    Remove an organisation from a sharing group

    Args:
      auth: Authentication details
      db: Database session.
      id: ID of the sharing group to remove the organisation
      organisation_id: ID of the organisation to remove

    Returns:
      Representation of the removed organisation from the sharing group
    """
    return await _remove_org_from_sharing_group(auth, db, id, organisation_id)


@router.patch(
    "/sharing_groups/{id}/servers",
    status_code=status.HTTP_200_OK,
    summary="Add a server",
)
@alog
async def add_server_to_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: AddServerToSharingGroupBody,
) -> dict:
    """
    Add a server to a sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to add the server
      body: Request body containing server details

    Returns:
      Representation of the added server in the sharing group
    """
    return await _add_server_to_sharing_group(auth, db, id, body)


@router.delete(
    "/sharing_groups/{id}/servers/{serverId}",
    status_code=status.HTTP_200_OK,
    summary="Remove a server",
)
@alog
async def remove_server_from_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    server_id: Annotated[int, Path(alias="serverId")],
) -> dict:
    """
    Remove a server from a sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to remove the server
      server_id: ID of the server to remove

    Returns:
      Representation of the removed server from the sharing group
    """
    return await _remove_server_from_sharing_group(auth, db, id, server_id)


# --- deprecated ---


@router.get(
    "/sharing_groups/view/{sharingGroupId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Get sharing groups details",
)
@alog
async def view_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int | uuid.UUID, Path(alias="sharingGroupId")],
) -> SingleSharingGroupResponse:
    """
    Retrieve details of a specific sharing group by its ID.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to retrieve

    Returns:
      Representation of the sharing group details
    """
    return await _view_sharing_group_legacy(auth, db, id)


@router.post(
    "/sharing_groups/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=CreateSharingGroupLegacyResponse,
)
@alog
async def create_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateSharingGroupLegacyBody,
) -> dict:
    """
    Add a new sharing group with given details.

    Args:
      auth: Authentication details
      db: Database session
      body: Request body containing details for creating the sharing group

    Returns:
      Representation of the created sharing group
    """
    return await _create_sharing_group_legacy(auth, db, body)


@router.post(
    "/sharing_groups/edit/{sharingGroupId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Update sharing group",
)
@alog
async def update_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    body: UpdateSharingGroupLegacyBody,
) -> ViewUpdateSharingGroupLegacyResponse:
    """
    Update an existing sharing group by its ID.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to update
      body: Request body containing updated details for the sharing group

    Returns:
      ViewUpdateSharingGroupLegacyResponse: Representation of the updated sharing group.
    """
    return await _update_sharing_group_legacy(auth, db, id, body)


@router.delete(
    "/sharing_groups/delete/{sharingGroupId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    summary="Delete sharing group",
)
@alog
async def delete_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
) -> dict:
    """
    Delete a specific sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to delete

    Returns:
      Representation of the deleted sharing group
    """
    return await _delete_sharing_group_legacy(auth, db, id)


@router.post(
    "/sharing_groups/addOrg/{sharingGroupId}/{organisationId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    summary="Add an organisation",
)
@alog
async def add_org_to_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    organisation_id: Annotated[int, Path(alias="organisationId")],
    body: AddOrgToSharingGroupLegacyBody = AddOrgToSharingGroupLegacyBody(),
) -> StandardStatusResponse:
    """
    Add an organisation to a sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to add the organisation
      organisation_id: ID of the organisation to add
      body: Request body containing additional details

    Returns:
      StandardStatusResponse: Response indicating success or failure
    """
    return await _add_org_to_sharing_group_legacy(auth, db, id, organisation_id, body)


@router.post(
    "/sharing_groups/removeOrg/{sharingGroupId}/{organisationId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    summary="Remove an organisation",
)
@alog
async def remove_org_from_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    organisation_id: Annotated[int, Path(alias="organisationId")],
) -> StandardStatusResponse:
    """
    Remove an organisation from a sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to remove the organisation from
      organisation_id: ID of the organisation to remove

    Returns:
      StandardStatusResponse: Response indicating success or failure
    """
    return await _remove_org_from_sharing_group_legacy(auth, db, id, organisation_id)


@router.post(
    "/sharing_groups/addServer/{sharingGroupId}/{serverId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    summary="Add a server",
)
@alog
async def add_server_to_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    server_id: Annotated[int, Path(alias="serverId")],
    body: AddServerToSharingGroupLegacyBody = AddServerToSharingGroupLegacyBody(),
) -> StandardStatusResponse:
    """
    Add a server to a sharing group.

    Args:
      auth: Authentication details
      db: Database session
      id: ID of the sharing group to add the server
      server_id: ID of the server to add
      body: Request body containing additional details

    Returns:
      StandardStatusResponse: Response indicating success or failure
    """
    return await _add_server_to_sharing_group_legacy(auth, db, id, server_id, body)


@router.post(
    "/sharing_groups/removeServer/{sharingGroupId}/{serverId}",
    deprecated=True,
    summary="Remove a server",
)
@alog
async def remove_server_from_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    server_id: Annotated[int, Path(alias="serverId")],
) -> StandardStatusResponse:
    """
    Remove a server from a sharing group.

    Args:
      auth: Authenticated user with 'SHARING_GROUP' permission
      db: Database session
      id: ID of the sharing group to remove the server from
      server_id: ID of the server to remove

    Returns:
      StandardStatusResponse: Response indicating success or failure
    """
    return await _remove_server_from_sharing_group_legacy(auth, db, id, server_id)


# ---endpoint logic ---


@alog
async def _create_sharing_group(auth: Auth, db: Session, body: CreateSharingGroupBody) -> dict:
    organisation: Organisation | None = None

    if body.organisation_uuid and check_permissions(auth, [Permission.SITE_ADMIN]):
        result = await db.execute(select(Organisation).filter(Organisation.uuid == body.organisation_uuid).limit(1))
        organisation = result.scalars().first()

    if organisation is None:
        organisation = await db.get(Organisation, auth.org_id)

    if organisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = SharingGroup(
        **{
            **body.model_dump(),
            # overwrite organisation_uuid with the correct one if not site admin
            "organisation_uuid": organisation.uuid,
            "org_id": organisation.id,
        },
    )

    db.add(sharing_group)
    await db.flush()
    await db.refresh(sharing_group)

    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=organisation.id, extend=True)
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0, all_orgs=False)

    db.add_all([sharing_group_org, sharing_group_server])
    await db.flush()
    await db.refresh(sharing_group)

    return sharing_group.asdict()


@alog
async def _get_sharing_group(auth: Auth, db: Session, id: int | uuid.UUID) -> dict:
    qry = select(SharingGroup).limit(1)
    if isinstance(id, int):
        qry = qry.filter(SharingGroup.id == id)
    else:
        qry = qry.filter(SharingGroup.uuid == id)

    sharing_group = (await db.execute(qry)).scalars().one_or_none()

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if sharing_group.org_id == auth.org_id or check_permissions(auth, [Permission.SITE_ADMIN]):
        return sharing_group.asdict()

    result = await db.execute(
        select(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == sharing_group.id, SharingGroupOrg.org_id == auth.org_id)
        .limit(1)
    )
    sharing_group_org: SharingGroupOrg | None = result.scalars().first()

    if sharing_group_org:
        return sharing_group.asdict()

    sharing_group_server: SharingGroupServer | None = None
    user_org: Organisation | None = await db.get(Organisation, auth.org_id)

    del result

    if user_org and user_org.local:
        result2 = await db.execute(
            select(SharingGroupServer)
            .filter(
                SharingGroupServer.sharing_group_id == id,
                SharingGroupServer.server_id == 0,
                SharingGroupServer.all_orgs.is_(True),
            )
            .limit(1)
        )
        sharing_group_server = result2.scalars().first()

    if sharing_group_server:
        return sharing_group.asdict()

    raise HTTPException(status.HTTP_404_NOT_FOUND)


@alog
async def _update_sharing_group(auth: Auth, db: Session, id: int, body: UpdateSharingGroupBody) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if sharing_group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group.patch(**body.model_dump(exclude_unset=True))

    await db.flush()
    await db.refresh(sharing_group)

    return sharing_group.asdict()


@alog
async def _delete_sharing_group(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if sharing_group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.execute(delete(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    await db.execute(delete(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id))

    await db.delete(sharing_group)
    await db.flush()

    return sharing_group.asdict()


def _process_sharing_group(sharing_group: SharingGroup) -> dict:
    organisation: Organisation | None = sharing_group.creator_org

    sharing_group_orgs: Sequence[SharingGroupOrg] = sharing_group.sharing_group_orgs
    sharing_group_servers: Sequence[SharingGroupServer] = sharing_group.sharing_group_servers

    sharing_group_orgs_computed = [
        {
            **sgo.asdict(),
            "Organisation": sgo.organisation.asdict(),
        }
        for sgo in sharing_group_orgs
    ]

    sharing_group_servers_computed: list[dict] = []

    for sgs in sharing_group_servers:
        sgs_server = LOCAL_INSTANCE_SERVER if sgs.server_id == 0 else sgs.server.asdict()

        sharing_group_servers_computed.append({**sgs.asdict(), "Server": sgs_server})

    return {
        "SharingGroup": {**sharing_group.asdict(), "org_count": len(sharing_group_orgs)},
        "Organisation": organisation.asdict() if organisation is not None else None,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
        "editable": True,
        "deletable": True,
    }


@alog
async def _get_all_sharing_groups(auth: Auth, db: Session) -> GetSharingGroupsIndex:
    qry = select(SharingGroup).options(
        selectinload(SharingGroup.creator_org),
        selectinload(SharingGroup.sharing_group_orgs).options(selectinload(SharingGroupOrg.organisation)),
        selectinload(SharingGroup.sharing_group_servers).options(selectinload(SharingGroupServer.server)),
    )
    result = await db.execute(qry)
    sharing_groups = result.scalars().all()

    return GetSharingGroupsIndex.model_validate({"response": [_process_sharing_group(sg) for sg in sharing_groups]})


@alog
async def _get_sharing_group_info(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        result = await db.execute(
            select(SharingGroupOrg)
            .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == auth.org_id)
            .limit(1)
        )
        sharing_group_org: SharingGroupOrg | None = result.scalars().first()

        sharing_group_server: SharingGroupServer | None = None
        user_org: Organisation | None = await db.get(Organisation, auth.org_id)

        if user_org and user_org.local:
            result2 = await db.execute(
                select(SharingGroupServer)
                .filter(
                    SharingGroupServer.sharing_group_id == id,
                    SharingGroupServer.server_id == 0,
                    SharingGroupServer.all_orgs.is_(True),
                )
                .limit(1)
            )
            sharing_group_server = result2.scalars().first()

        if not sharing_group_org and not sharing_group_server:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

    organisation: Organisation | None = await db.get(Organisation, sharing_group.org_id)

    result3 = await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    sharing_group_orgs: Sequence[SharingGroupOrg] = result3.scalars().all()

    result4 = await db.execute(
        select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id)
    )
    sharing_group_servers: Sequence[SharingGroupServer] = result4.scalars().all()

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation | None = await db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {
                **sharing_group_org.asdict(),
                "Organisation": sharing_group_org_organisation.asdict()
                if sharing_group_org_organisation is not None
                else None,
            }
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        sharing_group_server_server: Any | None = None

        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = await db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = (
                sharing_group_server_server.asdict() if sharing_group_server_server is not None else None
            )

        sharing_group_servers_computed.append({**sharing_group_server.asdict(), "Server": sharing_group_server_server})

    return {
        "SharingGroup": {**sharing_group.asdict(), "org_count": len(sharing_group_orgs)},
        "Organisation": organisation.asdict() if organisation is not None else None,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
    }


@alog
async def _add_org_to_sharing_group(
    auth: Auth, db: Session, id: int, body: AddOrgToSharingGroupBody
) -> SharingGroupOrgSchema:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == body.organisationId)
        .limit(1)
    )
    sharing_group_org: SharingGroupOrg | None = result.scalars().first()

    if not sharing_group_org:
        sharing_group_org = SharingGroupOrg(
            sharing_group_id=id,
            org_id=body.organisationId,
            extend=body.extend,
        )

        db.add(sharing_group_org)

    update = body.model_dump(exclude_unset=True)
    update.pop("organisationId")

    sharing_group_org.patch(**update)

    await db.flush()
    await db.refresh(sharing_group_org)

    return SharingGroupOrgSchema.model_validate(sharing_group_org.asdict())


@alog
async def _remove_org_from_sharing_group(auth: Auth, db: Session, id: int, organisation_id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == organisation_id)
        .limit(1)
    )
    sharing_group_org: SharingGroupOrg | None = result.scalars().first()

    if not sharing_group_org:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(sharing_group_org)
    await db.flush()

    return sharing_group_org.asdict()


@alog
async def _add_server_to_sharing_group(auth: Auth, db: Session, id: int, body: AddServerToSharingGroupBody) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == body.serverId)
        .limit(1)
    )
    sharing_group_server: SharingGroupServer | None = result.scalars().first()

    if not sharing_group_server:
        sharing_group_server = SharingGroupServer(
            sharing_group_id=id,
            server_id=body.serverId,
            all_orgs=body.all_orgs,
        )

        db.add(sharing_group_server)

    update = body.model_dump(exclude_unset=True)
    update.pop("serverId")

    sharing_group_server.patch(**update)

    await db.flush()
    await db.refresh(sharing_group_server)

    return sharing_group_server.asdict()


@alog
async def _remove_server_from_sharing_group(auth: Auth, db: Session, id: int, server_id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == server_id)
        .limit(1)
    )
    sharing_group_server: SharingGroupServer | None = result.scalars().first()

    if not sharing_group_server:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(sharing_group_server)
    await db.flush()

    return sharing_group_server.asdict()


@alog
async def _create_sharing_group_legacy(auth: Auth, db: Session, body: CreateSharingGroupLegacyBody) -> dict:
    organisation: Organisation | None = None

    is_site_admin = check_permissions(auth, [Permission.SITE_ADMIN])

    if body.organisation_uuid and is_site_admin:
        result = await db.execute(select(Organisation).filter(Organisation.uuid == body.organisation_uuid).limit(1))
        organisation = result.scalars().first()
    elif body.org_id and is_site_admin:
        organisation = await db.get(Organisation, body.org_id)

    if not organisation:
        organisation = await db.get(Organisation, auth.org_id)
    if organisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    create = body.model_dump(exclude={"org_count", "created", "modified", "sync_user_id"})

    sharing_group = SharingGroup(
        **{
            **create,
            # overwrite organisation_uuid with the correct one if not site admin
            "organisation_uuid": organisation.uuid,
            "org_id": organisation.id,
        },
    )

    db.add(sharing_group)
    await db.flush()
    await db.refresh(sharing_group)

    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=organisation.id, extend=True)
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0, all_orgs=False)

    db.add_all([sharing_group_org, sharing_group_server])
    await db.flush()
    await db.refresh(sharing_group_org)
    await db.refresh(sharing_group_server)
    await db.refresh(sharing_group)
    await db.refresh(organisation)

    return {
        "SharingGroup": sharing_group.asdict(),
        "Organisation": organisation.asdict(),
        "SharingGroupOrg": [sharing_group_org.asdict()],
        "SharingGroupServer": [sharing_group_server.asdict()],
    }


@alog
async def _view_sharing_group_legacy(auth: Auth, db: Session, id: int | uuid.UUID) -> SingleSharingGroupResponse:
    qry = (
        select(SharingGroup)
        .limit(1)
        .options(
            selectinload(SharingGroup.creator_org),
            selectinload(SharingGroup.sharing_group_orgs).options(selectinload(SharingGroupOrg.organisation)),
            selectinload(SharingGroup.sharing_group_servers).options(selectinload(SharingGroupServer.server)),
        )
    )
    if isinstance(id, int):
        qry = qry.filter(SharingGroup.id == id)
    else:
        qry = qry.filter(SharingGroup.uuid == id)

    sharing_group = (await db.execute(qry)).scalars().one_or_none()

    if sharing_group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    res = _process_sharing_group(sharing_group)

    return SingleSharingGroupResponse.model_validate(res)


@alog
async def _update_sharing_group_legacy(
    auth: Auth, db: Session, id: int, body: UpdateSharingGroupLegacyBody
) -> ViewUpdateSharingGroupLegacyResponse:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update = body.model_dump(
        include={"name", "description", "releasability", "local", "active", "roaming"}, exclude_unset=True
    )
    sharing_group.patch(**update)

    await db.flush()
    await db.refresh(sharing_group)

    organisation = await db.get(Organisation, sharing_group.org_id)

    result = await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    sharing_group_orgs: Sequence[SharingGroupOrg] = result.scalars().all()

    result2 = await db.execute(
        select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id)
    )
    sharing_group_servers: Sequence[SharingGroupServer] = result2.scalars().all()

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation | None = await db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {
                **sharing_group_org.asdict(),
                "Organisation": sharing_group_org_organisation.asdict()
                if sharing_group_org_organisation is not None
                else None,
            }
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        sharing_group_server_server: Any | None = None

        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = await db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = (
                sharing_group_server_server.asdict() if sharing_group_server_server is not None else None
            )

        sharing_group_servers_computed.append({**sharing_group_server.asdict(), "Server": sharing_group_server_server})

    return ViewUpdateSharingGroupLegacyResponse.model_validate(
        {
            "SharingGroup": sharing_group.asdict(),
            "Organisation": organisation.asdict() if organisation is not None else None,
            "SharingGroupOrg": sharing_group_orgs_computed,
            "SharingGroupServer": sharing_group_servers_computed,
        }
    )


@alog
async def _delete_sharing_group_legacy(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.execute(delete(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    await db.execute(delete(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id))

    await db.delete(sharing_group)
    await db.flush()

    return {
        "id": sharing_group.id,
        "saved": True,
        "success": True,
        "name": "Organisation removed from the sharing group.",
        "message": "Organisation removed from the sharing group.",
        "url": "/sharing_groups/removeOrg",
    }


@alog
async def _add_org_to_sharing_group_legacy(
    auth: Auth, db: Session, id: int, organisation_id: int, body: AddOrgToSharingGroupLegacyBody
) -> StandardStatusResponse:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == organisation_id)
        .limit(1)
    )
    sharing_group_org: SharingGroupOrg | None = result.scalars().first()

    if not sharing_group_org:
        sharing_group_org = SharingGroupOrg(
            sharing_group_id=id,
            org_id=organisation_id,
            extend=body.extend,
        )

        db.add(sharing_group_org)

    sharing_group_org.patch(**body.model_dump(exclude_unset=True))

    await db.flush()
    await db.refresh(sharing_group_org)

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Organisation added to the sharing group.",
        message="Organisation added to the sharing group.",
        url="/sharing_groups/addOrg",
    )


@alog
async def _remove_org_from_sharing_group_legacy(
    auth: Auth, db: Session, id: int, organisation_id: int
) -> StandardStatusResponse:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == organisation_id)
        .limit(1)
    )
    sharing_group_org: SharingGroupOrg | None = result.scalars().first()

    if not sharing_group_org:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(sharing_group_org)
    await db.flush()

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Organisation removed from the sharing group.",
        message="Organisation removed from the sharing group.",
        url="/sharing_groups/removeOrg",
    )


@alog
async def _add_server_to_sharing_group_legacy(
    auth: Auth, db: Session, id: int, server_id: int, body: AddServerToSharingGroupLegacyBody
) -> StandardStatusResponse:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == server_id)
        .limit(1)
    )
    sharing_group_server: SharingGroupServer | None = result.scalars().first()

    if not sharing_group_server:
        sharing_group_server = SharingGroupServer(
            sharing_group_id=id,
            server_id=server_id,
            all_orgs=body.all_orgs,
        )

        db.add(sharing_group_server)

    sharing_group_server.patch(**body.model_dump(exclude_unset=True))

    await db.flush()
    await db.refresh(sharing_group_server)

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Server added to the sharing group.",
        message="Server added to the sharing group.",
        url="/sharing_groups/addServer",
    )


@alog
async def _remove_server_from_sharing_group_legacy(
    auth: Auth, db: Session, id: int, server_id: int
) -> StandardStatusResponse:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == server_id)
        .limit(1)
    )
    sharing_group_server: SharingGroupServer | None = result.scalars().first()

    if not sharing_group_server:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(sharing_group_server)
    await db.flush()

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Server removed from the sharing group.",
        message="Server removed from the sharing group.",
        url="/sharing_groups/removeServer",
    )
