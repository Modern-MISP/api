from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import and_, delete, or_
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.sharing_groups.add_org_to_sharing_group_body import AddOrgToSharingGroupBody
from mmisp.api_schemas.sharing_groups.add_org_to_sharing_group_legacy_body import AddOrgToSharingGroupLegacyBody
from mmisp.api_schemas.sharing_groups.add_server_to_sharing_group_body import AddServerToSharingGroupBody
from mmisp.api_schemas.sharing_groups.add_server_to_sharing_group_legacy_body import AddServerToSharingGroupLegacyBody
from mmisp.api_schemas.sharing_groups.create_sharing_group_body import CreateSharingGroupBody
from mmisp.api_schemas.sharing_groups.create_sharing_group_legacy_body import CreateSharingGroupLegacyBody
from mmisp.api_schemas.sharing_groups.create_sharing_group_legacy_response import CreateSharingGroupLegacyResponse
from mmisp.api_schemas.sharing_groups.delete_sharing_group_legacy_response import DeleteSharingGroupLegacyResponse
from mmisp.api_schemas.sharing_groups.get_all_sharing_groups_response import GetAllSharingGroupsResponse
from mmisp.api_schemas.sharing_groups.get_sharing_group_info_response import GetSharingGroupInfoResponse
from mmisp.api_schemas.sharing_groups.sharing_group import SharingGroup as SharingGroupSchema
from mmisp.api_schemas.sharing_groups.sharing_group_org import SharingGroupOrg as SharingGroupOrgSchema
from mmisp.api_schemas.sharing_groups.sharing_group_server import SharingGroupServer as SharingGroupServerSchema
from mmisp.api_schemas.sharing_groups.update_sharing_group_body import UpdateSharingGroupBody
from mmisp.api_schemas.sharing_groups.update_sharing_group_legacy_body import UpdateSharingGroupLegacyBody
from mmisp.api_schemas.sharing_groups.view_update_sharing_group_legacy_response import (
    ViewUpdateSharingGroupLegacyResponse,
)
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from mmisp.config import config
from mmisp.db.database import Session, get_db, with_session_management
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.server import Server
from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from mmisp.util.models import update_record
from mmisp.util.partial import partial

router = APIRouter(tags=["sharing_groups"])

LOCAL_INSTANCE_SERVER = {"id": 0, "name": "Local instance", "url": config.OWN_URL}


@router.post(
    "/sharing_groups",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SharingGroupSchema),
    summary="Add a new sharing group",
    description="Add a new sharing group with given details.",
)
@with_session_management
async def create_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateSharingGroupBody,
) -> dict:
    return await _create_sharing_group(auth, db, body)


@router.get(
    "/sharing_groups/{id}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SharingGroupSchema),
    summary="Get sharing group details",
    description="Retrieve details of a specific sharing group.",
)
@with_session_management
async def get_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    return await _get_sharing_group(auth, db, id)


@router.put(
    "/sharing_groups/{id}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SharingGroupSchema),
    summary="Update sharing group",
    description="Update an existing sharing group.",
)
@with_session_management
async def update_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: UpdateSharingGroupBody,
) -> dict:
    return await _update_sharing_group(auth, db, id, body)


@router.delete(
    "/sharing_groups/{id}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SharingGroupSchema),
    summary="Delete sharing group",
    description="Delete a specific sharing group.",
)
@with_session_management
async def delete_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    return await _delete_sharing_group(auth, db, id)


@router.get(
    "/sharing_groups",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetAllSharingGroupsResponse),
    summary="Get all sharing groups",
    description="Retrieve a list of all sharing groups.",
)
@with_session_management
async def get_all_sharing_groups(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _get_all_sharing_groups(auth, db)


@router.get(
    "/sharing_groups/{id}/info",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetSharingGroupInfoResponse),
    summary="Additional infos from a sharing group",
    description="Details of a sharing group and org.count, user_count and created_by_email.",
)
@with_session_management
async def get_sharing_group_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    return await _get_sharing_group_info(auth, db, id)


@router.patch(
    "/sharing_groups/{id}/organisations",
    status_code=status.HTTP_200_OK,
    response_model=partial(SharingGroupOrgSchema),
    summary="Add an organisation",
    description="Add an organisation to a sharing group.",
)
@with_session_management
async def add_org_to_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: AddOrgToSharingGroupBody,
) -> dict:
    return await _add_org_to_sharing_group(auth, db, id, body)


@router.delete(
    "/sharing_groups/{id}/organisations/{organisationId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SharingGroupOrgSchema),
    summary="Remove an organisation",
    description="Remove an organisation from a sharing group.",
)
@with_session_management
async def remove_org_from_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    organisation_id: Annotated[int, Path(alias="organisationId")],
) -> dict:
    return await _remove_org_from_sharing_group(auth, db, id, organisation_id)


@router.patch(
    "/sharing_groups/{id}/servers",
    status_code=status.HTTP_200_OK,
    response_model=partial(SharingGroupServerSchema),
    summary="Add a server",
    description="Add a server to a sharing group.",
)
@with_session_management
async def add_server_to_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: AddServerToSharingGroupBody,
) -> dict:
    return await _add_server_to_sharing_group(auth, db, id, body)


@router.delete(
    "/sharing_groups/{id}/servers/{serverId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SharingGroupServerSchema),
    summary="Remove a server",
    description="Remove a server from a sharing group.",
)
@with_session_management
async def remove_server_from_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    server_id: Annotated[int, Path(alias="serverId")],
) -> dict:
    return await _remove_server_from_sharing_group(auth, db, id, server_id)


# --- deprecated ---


@router.post(
    "/sharing_groups/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=partial(CreateSharingGroupLegacyResponse),
    summary="Add new sharing group",
    description="Add a new sharing group with given details.",
)
@with_session_management
async def create_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateSharingGroupLegacyBody,
) -> dict:
    return await _create_sharing_group_legacy(auth, db, body)


@router.get(
    "/sharing_groups/view/{sharingGroupId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(ViewUpdateSharingGroupLegacyResponse),
    summary="Get sharing groups details",
    description="Retrieve details of a specific sharing group by its ID.",
)
@with_session_management
async def view_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
) -> dict:
    return await _view_sharing_group_legacy(auth, db, id)


@router.post(
    "/sharing_groups/edit/{sharingGroupId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(ViewUpdateSharingGroupLegacyResponse),
    summary="Update sharing group",
    description="Update an existing sharing group by its ID.",
)
@with_session_management
async def update_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    body: UpdateSharingGroupLegacyBody,
) -> dict:
    return await _update_sharing_group_legacy(auth, db, id, body)


@router.delete(
    "/sharing_groups/delete/{sharingGroupId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    response_model=partial(DeleteSharingGroupLegacyResponse),
    summary="Delete sharing group",
    description="Delete a specific sharing group.",
)
@with_session_management
async def delete_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
) -> dict:
    return await _delete_sharing_group_legacy(auth, db, id)


@router.post(
    "/sharing_groups/addOrg/{sharingGroupId}/{organisationId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    response_model=partial(StandardStatusResponse),
    summary="Add an organisation",
    description="Add an organisation to a sharing group.",
)
@with_session_management
async def add_org_to_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    organisation_id: Annotated[int, Path(alias="organisationId")],
    body: AddOrgToSharingGroupLegacyBody = AddOrgToSharingGroupLegacyBody(),
) -> dict:
    return await _add_org_to_sharing_group_legacy(auth, db, id, organisation_id, body)


@router.post(
    "/sharing_groups/removeOrg/{sharingGroupId}/{organisationId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    response_model=partial(StandardStatusResponse),
    summary="Remove an organisation",
    description="Remove an organisation from a sharing group.",
)
@with_session_management
async def remove_org_from_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    organisation_id: Annotated[int, Path(alias="organisationId")],
) -> dict:
    return await _remove_org_from_sharing_group_legacy(auth, db, id, organisation_id)


@router.post(
    "/sharing_groups/addServer/{sharingGroupId}/{serverId}",
    status_code=status.HTTP_200_OK,
    deprecated=True,
    response_model=partial(StandardStatusResponse),
    summary="Add a server",
    description="Add a server to a sharing group.",
)
@with_session_management
async def add_server_to_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    server_id: Annotated[int, Path(alias="serverId")],
    body: AddServerToSharingGroupLegacyBody = AddServerToSharingGroupLegacyBody(),
) -> dict:
    return await _add_server_to_sharing_group_legacy(auth, db, id, server_id, body)


@router.post(
    "/sharing_groups/removeServer/{sharingGroupId}/{serverId}",
    deprecated=True,
    response_model=partial(StandardStatusResponse),
    summary="Remove a server",
    description="Remove a server to a sharing group.",
)
@with_session_management
async def remove_server_from_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    server_id: Annotated[int, Path(alias="serverId")],
) -> dict:
    return await _remove_server_from_sharing_group_legacy(auth, db, id, server_id)


# ---endpoint logic ---


async def _create_sharing_group(auth: Auth, db: Session, body: CreateSharingGroupBody) -> dict:
    organisation: Organisation | None = None

    if body.organisation_uuid and await check_permissions(auth, [Permission.SITE_ADMIN]):
        result = await db.execute(select(Organisation).filter(Organisation.uuid == body.organisation_uuid).limit(1))
        organisation = result.scalars().first()

    if not organisation:
        organisation = await db.get(Organisation, auth.org_id)

    sharing_group = SharingGroup(
        **{
            **body.dict(),
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
    await db.commit()
    await db.refresh(sharing_group)

    return sharing_group.__dict__


async def _get_sharing_group(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id == auth.org_id or await check_permissions(auth, [Permission.SITE_ADMIN]):
        return sharing_group.__dict__

    result = await db.execute(
        select(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == sharing_group.id, SharingGroupOrg.org_id == auth.org_id)
        .limit(1)
    )
    sharing_group_org: SharingGroupOrg | None = result.scalars().first()

    if sharing_group_org:
        return sharing_group.__dict__

    sharing_group_server: SharingGroupServer | None = None
    user_org: Organisation | None = await db.get(Organisation, auth.org_id)

    if user_org and user_org.local:
        result = await db.execute(
            select(SharingGroupServer)
            .filter(
                SharingGroupServer.sharing_group_id == id,
                SharingGroupServer.server_id == 0,
                SharingGroupServer.all_orgs.is_(True),
            )
            .limit(1)
        )
        sharing_group_server = result.scalars().first()

    if sharing_group_server:
        return sharing_group.__dict__

    raise HTTPException(status.HTTP_404_NOT_FOUND)


async def _update_sharing_group(auth: Auth, db: Session, id: int, body: UpdateSharingGroupBody) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update_record(sharing_group, body.dict())

    await db.commit()
    await db.refresh(sharing_group)

    return sharing_group.__dict__


async def _delete_sharing_group(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.execute(delete(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    await db.execute(delete(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id))

    await db.delete(sharing_group)
    await db.commit()

    return sharing_group.__dict__


async def _get_all_sharing_groups(auth: Auth, db: Session) -> dict:
    sharing_groups: list[SharingGroup] = []

    is_site_admin: bool = await check_permissions(auth, [Permission.SITE_ADMIN])

    if is_site_admin:
        result = await db.execute(select(SharingGroup))
        sharing_groups = result.scalars().all()
    else:
        user_org: Organisation | None = await db.get(Organisation, auth.org_id)
        result = await db.execute(
            select(SharingGroup)
            .join(
                SharingGroupOrg,
                SharingGroup.id == SharingGroupOrg.sharing_group_id,
                isouter=True,
            )
            .join(
                SharingGroupServer,
                SharingGroup.id == SharingGroupServer.sharing_group_id,
                isouter=True,
            )
            .filter(
                or_(
                    SharingGroupOrg.org_id == auth.org_id,
                    SharingGroup.org_id == auth.org_id,
                    and_(SharingGroupServer.server_id == 0, SharingGroupServer.all_orgs.is_(True))
                    if user_org and user_org.local
                    else None,
                )
            )
        )
        sharing_groups = result.scalars().all()

    sharing_groups_computed: list[dict] = []

    for sharing_group in sharing_groups:
        organisation: Organisation = await db.get(Organisation, sharing_group.org_id)

        result = await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
        sharing_group_orgs: list[SharingGroupOrg] = result.scalars().all()

        result = await db.execute(
            select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id)
        )
        sharing_group_servers: list[SharingGroupServer] = result.scalars().all()

        sharing_group_orgs_computed: list[dict] = []

        for sharing_group_org in sharing_group_orgs:
            sharing_group_org_organisation: Organisation = await db.get(Organisation, sharing_group_org.org_id)

            sharing_group_orgs_computed.append(
                {
                    **sharing_group_org.__dict__,
                    "Organisation": getattr(sharing_group_org_organisation, "__dict__", None),
                }
            )

        sharing_group_servers_computed: list[dict] = []

        for sharing_group_server in sharing_group_servers:
            sharing_group_server_server: Any | None = None

            if sharing_group_server.server_id == 0:
                sharing_group_server_server = LOCAL_INSTANCE_SERVER
            else:
                sharing_group_server_server = await db.get(Server, sharing_group_server.server_id)
                sharing_group_server_server = getattr(sharing_group_server_server, "__dict__", None)

            sharing_group_servers_computed.append(
                {**sharing_group_server.__dict__, "Server": sharing_group_server_server}
            )

        sharing_groups_computed.append(
            {
                "SharingGroup": {**sharing_group.__dict__, "org_count": len(sharing_group_orgs)},
                "Organisation": organisation.__dict__,
                "SharingGroupOrg": sharing_group_orgs_computed,
                "SharingGroupServer": sharing_group_servers_computed,
                "editable": sharing_group.org_id == auth.org_id or is_site_admin,
                "deletable": sharing_group.org_id == auth.org_id or is_site_admin,
            }
        )

    return {"response": sharing_groups_computed}


async def _get_sharing_group_info(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN]):
        result = await db.execute(
            select(SharingGroupOrg)
            .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == auth.org_id)
            .limit(1)
        )
        sharing_group_org: SharingGroupOrg | None = result.scalars().first()

        sharing_group_server: SharingGroupServer | None = None
        user_org: Organisation | None = await db.get(Organisation, auth.org_id)

        if user_org and user_org.local:
            result = await db.execute(
                select(SharingGroupServer)
                .filter(
                    SharingGroupServer.sharing_group_id == id,
                    SharingGroupServer.server_id == 0,
                    SharingGroupServer.all_orgs.is_(True),
                )
                .limit(1)
            )
            sharing_group_server = result.scalars().first()

        if not sharing_group_org and not sharing_group_server:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

    organisation: Organisation = await db.get(Organisation, sharing_group.org_id)

    result = await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    sharing_group_orgs: list[SharingGroupOrg] = result.scalars().all()

    await db.execute(select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id))
    sharing_group_servers: list[SharingGroupServer] = result.scalars().all()

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation = await db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {**sharing_group_org.__dict__, "Organisation": getattr(sharing_group_org_organisation, "__dict__", None)}
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        sharing_group_server_server: Any | None = None

        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = await db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = getattr(sharing_group_server_server, "__dict__", None)

        sharing_group_servers_computed.append({**sharing_group_server.__dict__, "Server": sharing_group_server_server})

    return {
        "SharingGroup": {**sharing_group.__dict__, "org_count": len(sharing_group_orgs)},
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
    }


async def _add_org_to_sharing_group(auth: Auth, db: Session, id: int, body: AddOrgToSharingGroupBody) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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

    update = body.dict()
    update.pop("organisationId")

    update_record(sharing_group_org, update)

    await db.commit()
    await db.refresh(sharing_group_org)

    return sharing_group_org.__dict__


async def _remove_org_from_sharing_group(auth: Auth, db: Session, id: int, organisation_id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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
    await db.commit()

    return sharing_group_org.__dict__


async def _add_server_to_sharing_group(auth: Auth, db: Session, id: int, body: AddServerToSharingGroupBody) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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

    update = body.dict()
    update.pop("serverId")

    update_record(sharing_group_server, update)

    await db.commit()
    await db.refresh(sharing_group_server)

    return sharing_group_server.__dict__


async def _remove_server_from_sharing_group(auth: Auth, db: Session, id: int, server_id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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
    await db.commit()

    return sharing_group_server.__dict__


async def _create_sharing_group_legacy(auth: Auth, db: Session, body: CreateSharingGroupLegacyBody) -> dict:
    organisation: Organisation | None = None

    is_site_admin = await check_permissions(auth, [Permission.SITE_ADMIN])

    if body.organisation_uuid and is_site_admin:
        result = await db.execute(select(Organisation).filter(Organisation.uuid == body.organisation_uuid).limit(1))
        organisation = result.scalars().first()
    elif body.org_id and is_site_admin:
        organisation = await db.get(Organisation, body.org_id)

    if not organisation:
        organisation = await db.get(Organisation, auth.org_id)

    create = body.dict(exclude={"org_count", "created", "modified", "sync_user_id"})

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
    await db.commit()
    await db.refresh(sharing_group_org)
    await db.refresh(sharing_group_server)
    await db.refresh(sharing_group)
    await db.refresh(organisation)

    return {
        "SharingGroup": sharing_group.__dict__,
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": [sharing_group_org.__dict__],
        "SharingGroupServer": [sharing_group_server.__dict__],
    }


async def _view_sharing_group_legacy(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN]):
        result = await db.execute(
            select(SharingGroupOrg)
            .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == auth.org_id)
            .limit(1)
        )
        sharing_group_org: SharingGroupOrg | None = result.scalars().first()

        sharing_group_server: SharingGroupServer | None = None
        user_org: Organisation | None = await db.get(Organisation, auth.org_id)

        if user_org and user_org.local:
            result = await db.execute(
                select(SharingGroupServer)
                .filter(
                    SharingGroupServer.sharing_group_id == id,
                    SharingGroupServer.server_id == 0,
                    SharingGroupServer.all_orgs.is_(True),
                )
                .limit(1)
            )
            sharing_group_server = result.scalars().first()

        if not sharing_group_org and not sharing_group_server:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

    organisation: Organisation = await db.get(Organisation, sharing_group.org_id)

    result = await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    sharing_group_orgs: list[SharingGroupOrg] = result.scalars().all()

    result = await db.execute(
        select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id)
    )
    sharing_group_servers: list[SharingGroupServer] = result.scalars().all()

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation = await db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {**sharing_group_org.__dict__, "Organisation": getattr(sharing_group_org_organisation, "__dict__", None)}
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        sharing_group_server_server: Any | None = None

        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = await db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = getattr(sharing_group_server_server, "__dict__", None)

        sharing_group_servers_computed.append({**sharing_group_server.__dict__, "Server": sharing_group_server_server})

    return {
        "SharingGroup": sharing_group.__dict__,
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
    }


async def _update_sharing_group_legacy(auth: Auth, db: Session, id: int, body: UpdateSharingGroupBody) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update = body.dict(include={"name", "description", "releasability", "local", "active", "roaming"})
    update_record(sharing_group, update)

    await db.commit()
    await db.refresh(sharing_group)

    organisation = await db.get(Organisation, sharing_group.org_id)

    result = await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    sharing_group_orgs: list[SharingGroupOrg] = result.scalars().all()

    result = await db.execute(
        select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id)
    )
    sharing_group_servers: list[SharingGroupServer] = result.scalars().all()

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation = await db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {**sharing_group_org.__dict__, "Organisation": getattr(sharing_group_org_organisation, "__dict__", None)}
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        sharing_group_server_server: Any | None = None

        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = await db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = getattr(sharing_group_server_server, "__dict__", None)

        sharing_group_servers_computed.append({**sharing_group_server.__dict__, "Server": sharing_group_server_server})

    return {
        "SharingGroup": sharing_group.__dict__,
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
    }


async def _delete_sharing_group_legacy(auth: Auth, db: Session, id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.execute(delete(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id))
    await db.execute(delete(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id))

    await db.delete(sharing_group)
    await db.commit()

    return {
        "id": sharing_group.id,
        "saved": True,
        "success": True,
        "name": "Organisation removed from the sharing group.",
        "message": "Organisation removed from the sharing group.",
        "url": "/sharing_groups/removeOrg",
    }


async def _add_org_to_sharing_group_legacy(
    auth: Auth, db: Session, id: int, organisation_id: int, body: AddOrgToSharingGroupBody
) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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

    update_record(sharing_group_org, body.dict())

    await db.commit()
    await db.refresh(sharing_group_org)

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Organisation added to the sharing group.",
        message="Organisation added to the sharing group.",
        url="/sharing_groups/addOrg",
    )


async def _remove_org_from_sharing_group_legacy(auth: Auth, db: Session, id: int, organisation_id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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
    await db.commit()

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Organisation removed from the sharing group.",
        message="Organisation removed from the sharing group.",
        url="/sharing_groups/removeOrg",
    )


async def _add_server_to_sharing_group_legacy(
    auth: Auth, db: Session, id: int, server_id: int, body: AddServerToSharingGroupBody
) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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

    update_record(sharing_group_server, body.dict())

    await db.commit()
    await db.refresh(sharing_group_server)

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Server added to the sharing group.",
        message="Server added to the sharing group.",
        url="/sharing_groups/addServer",
    )


async def _remove_server_from_sharing_group_legacy(auth: Auth, db: Session, id: int, server_id: int) -> dict:
    sharing_group: SharingGroup | None = await db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not await check_permissions(auth, [Permission.SITE_ADMIN])
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
    await db.commit()

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Server removed from the sharing group.",
        message="Server removed from the sharing group.",
        url="/sharing_groups/removeServer",
    )
