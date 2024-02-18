from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

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
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.server import Server
from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from mmisp.util.models import update_record
from mmisp.util.partial import partial

router = APIRouter(tags=["sharing_groups"])

LOCAL_INSTANCE_SERVER = {"id": 0, "name": "Local instance", "url": config.OWN_URL}


@router.post("/sharing_groups", status_code=status.HTTP_201_CREATED, response_model=partial(SharingGroupSchema))
@with_session_management
async def create_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateSharingGroupBody,
) -> dict:
    organisation: Organisation | None = None

    if body.organisation_uuid is not None and check_permissions(auth, [Permission.SITE_ADMIN]):
        organisation = db.query(Organisation).filter(Organisation.uuid == body.organisation_uuid).first()

    if not organisation:
        organisation = db.get(Organisation, auth.org_id)

    sharing_group = SharingGroup(
        **{
            **body.dict(),
            # overwrite organisation_uuid with the correct one if not site admin
            "organisation_uuid": organisation.uuid,
            "org_id": organisation.id,
            "sync_user_id": auth.user_id,
        },
    )

    db.add(sharing_group)
    db.flush()
    db.refresh(sharing_group)

    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=organisation.id, extend=True)
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0, all_orgs=False)

    db.add_all([sharing_group_org, sharing_group_server])
    db.commit()
    db.refresh(sharing_group)

    return sharing_group.__dict__


@router.get("/sharing_groups/{id}", response_model=partial(SharingGroupSchema))
@with_session_management
async def get_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(404)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id == auth.org_id or check_permissions(auth, [Permission.SITE_ADMIN]):
        return sharing_group.__dict__

    sharing_group_org: SharingGroupOrg | None = (
        db.query(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == sharing_group.id, SharingGroupOrg.org_id == auth.org_id)
        .first()
    )

    if sharing_group_org:
        return sharing_group.__dict__

    sharing_group_server: SharingGroupServer | None = None
    user_org: Organisation | None = db.get(Organisation, auth.org_id)

    if user_org and user_org.local:
        sharing_group_server = (
            db.query(SharingGroupServer)
            .filter(
                SharingGroupServer.sharing_group_id == id,
                SharingGroupServer.server_id == 0,
                SharingGroupServer.all_orgs.is_(True),
            )
            .first()
        )

    if sharing_group_server:
        return sharing_group.__dict__

    raise HTTPException(404)


@router.put("/sharing_groups/{id}", response_model=partial(SharingGroupSchema))
@with_session_management
async def update_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: UpdateSharingGroupBody,
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(404)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(404)

    update_record(sharing_group, body.dict())

    db.commit()
    db.refresh(sharing_group)

    return sharing_group.__dict__


@router.delete("/sharing_groups/{id}", response_model=partial(SharingGroupSchema))
@with_session_management
async def delete_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(404)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(404)

    db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id).delete(False)
    db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id).delete(False)

    db.delete(sharing_group)
    db.commit()

    return sharing_group.__dict__


@router.get("/sharing_groups", response_model=partial(GetAllSharingGroupsResponse))
@with_session_management
async def get_all_sharing_groups(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    sharing_groups: list[SharingGroup] = []

    is_site_admin: bool = check_permissions(auth, [Permission.SITE_ADMIN])

    if is_site_admin:
        sharing_groups = db.query(SharingGroup).all()
    else:
        user_org: Organisation | None = db.get(Organisation, auth.org_id)
        sharing_groups = (
            db.query(SharingGroup)
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
            .all()
        )

    sharing_groups_computed: list[dict] = []

    for sharing_group in sharing_groups:
        organisation: Organisation = db.get(Organisation, sharing_group.org_id)
        sharing_group_orgs: list[SharingGroupOrg] = (
            db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id).all()
        )
        sharing_group_servers: list[SharingGroupServer] = (
            db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id).all()
        )

        sharing_group_orgs_computed: list[dict] = []

        for sharing_group_org in sharing_group_orgs:
            sharing_group_org_organisation: Organisation = db.get(Organisation, sharing_group_org.org_id)

            sharing_group_orgs_computed.append(
                {
                    **sharing_group_org.__dict__,
                    "Organisation": getattr(sharing_group_org_organisation, "__dict__", None),
                }
            )

        sharing_group_servers_computed: list[dict] = []

        for sharing_group_server in sharing_group_servers:
            if sharing_group_server.server_id == 0:
                sharing_group_server_server = LOCAL_INSTANCE_SERVER
            else:
                sharing_group_server_server = db.get(Server, sharing_group_server.server_id)
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


@router.get("/sharing_groups/{id}/info", response_model=partial(GetSharingGroupInfoResponse))
@with_session_management
async def get_sharing_group_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(404)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        sharing_group_org: SharingGroupOrg | None = (
            db.query(SharingGroupOrg)
            .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == auth.org_id)
            .first()
        )

        sharing_group_server: SharingGroupServer | None = None
        user_org: Organisation | None = db.get(Organisation, auth.org_id)

        if user_org and user_org.local:
            sharing_group_server = (
                db.query(SharingGroupServer)
                .filter(
                    SharingGroupServer.sharing_group_id == id,
                    SharingGroupServer.server_id == 0,
                    SharingGroupServer.all_orgs.is_(True),
                )
                .first()
            )

        if not sharing_group_org and not sharing_group_server:
            raise HTTPException(404)

    organisation: Organisation = db.get(Organisation, sharing_group.org_id)
    sharing_group_orgs: list[SharingGroupOrg] = (
        db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id).all()
    )
    sharing_group_servers: list[SharingGroupServer] = (
        db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id).all()
    )

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation = db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {**sharing_group_org.__dict__, "Organisation": getattr(sharing_group_org_organisation, "__dict__", None)}
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = getattr(sharing_group_server_server, "__dict__", None)

        sharing_group_servers_computed.append({**sharing_group_server.__dict__, "Server": sharing_group_server_server})

    return {
        "SharingGroup": {**sharing_group.__dict__, "org_count": len(sharing_group_orgs)},
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
    }


@router.patch("/sharing_groups/{id}/organisations", response_model=partial(SharingGroupOrgSchema))
@with_session_management
async def add_org_to_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: AddOrgToSharingGroupBody,
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_org: SharingGroupOrg | None = (
        db.query(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == body.organisationId)
        .first()
    )

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

    db.commit()
    db.refresh(sharing_group_org)

    return sharing_group_org.__dict__


@router.delete("/sharing_groups/{id}/organisations/{organisationId}", response_model=partial(SharingGroupOrgSchema))
@with_session_management
async def remove_org_from_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    organisation_id: Annotated[int, Path(alias="organisationId")],
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_org: SharingGroupOrg | None = (
        db.query(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == organisation_id)
        .first()
    )

    if not sharing_group_org:
        raise HTTPException(404)

    db.delete(sharing_group_org)
    db.commit()

    return sharing_group_org.__dict__


@router.patch("/sharing_groups/{id}/servers", response_model=partial(SharingGroupServerSchema))
@with_session_management
async def add_server_to_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    body: AddServerToSharingGroupBody,
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_server: SharingGroupServer | None = (
        db.query(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == body.serverId)
        .first()
    )

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

    db.commit()
    db.refresh(sharing_group_server)

    return sharing_group_server.__dict__


@router.delete("/sharing_groups/{id}/servers/{serverId}", response_model=partial(SharingGroupServerSchema))
@with_session_management
async def remove_server_from_sharing_group(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    server_id: Annotated[int, Path(alias="serverId")],
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_server: SharingGroupServer | None = (
        db.query(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == server_id)
        .first()
    )

    if not sharing_group_server:
        raise HTTPException(404)

    db.delete(sharing_group_server)
    db.commit()

    return sharing_group_server.__dict__


# --- deprecated ---


@router.post(
    "/sharing_groups/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=partial(CreateSharingGroupLegacyResponse),
)
@with_session_management
async def create_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateSharingGroupLegacyBody,
) -> dict:
    organisation: Organisation | None = None

    is_site_admin = check_permissions(auth, [Permission.SITE_ADMIN])

    if body.organisation_uuid is not None and is_site_admin:
        organisation = db.query(Organisation).filter(Organisation.uuid == body.organisation_uuid).first()
    elif body.org_id is not None and is_site_admin:
        organisation = db.get(Organisation, body.org_id)

    if not organisation:
        organisation = db.get(Organisation, auth.org_id)

    create = body.dict()
    create.pop("org_count")
    create.pop("created")
    create.pop("modified")

    sharing_group = SharingGroup(
        **{
            **create,
            # overwrite organisation_uuid with the correct one if not site admin
            "organisation_uuid": organisation.uuid,
            "org_id": organisation.id,
            "sync_user_id": auth.user_id,
        },
    )

    db.add(sharing_group)
    db.flush()
    db.refresh(sharing_group)

    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=organisation.id, extend=True)
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0, all_orgs=False)

    db.add_all([sharing_group_org, sharing_group_server])
    db.commit()
    db.refresh(sharing_group_org)
    db.refresh(sharing_group_server)
    db.refresh(sharing_group)
    db.refresh(organisation)

    return {
        "SharingGroup": sharing_group.__dict__,
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": [sharing_group_org.__dict__],
        "SharingGroupServer": [sharing_group_server.__dict__],
    }


@router.get(
    "/sharing_groups/view/{sharingGroupId}",
    deprecated=True,
    response_model=partial(ViewUpdateSharingGroupLegacyResponse),
)
@with_session_management
async def view_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        sharing_group_org: SharingGroupOrg | None = (
            db.query(SharingGroupOrg)
            .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == auth.org_id)
            .first()
        )

        sharing_group_server: SharingGroupServer | None = None
        user_org: Organisation | None = db.get(Organisation, auth.org_id)

        if user_org and user_org.local:
            sharing_group_server = (
                db.query(SharingGroupServer)
                .filter(
                    SharingGroupServer.sharing_group_id == id,
                    SharingGroupServer.server_id == 0,
                    SharingGroupServer.all_orgs.is_(True),
                )
                .first()
            )

        if not sharing_group_org and not sharing_group_server:
            raise HTTPException(404)

    organisation: Organisation = db.get(Organisation, sharing_group.org_id)
    sharing_group_orgs: list[SharingGroupOrg] = (
        db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id).all()
    )
    sharing_group_servers: list[SharingGroupServer] = (
        db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id).all()
    )

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation = db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {**sharing_group_org.__dict__, "Organisation": getattr(sharing_group_org_organisation, "__dict__", None)}
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = getattr(sharing_group_server_server, "__dict__", None)

        sharing_group_servers_computed.append({**sharing_group_server.__dict__, "Server": sharing_group_server_server})

    return {
        "SharingGroup": sharing_group.__dict__,
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
    }


@router.post(
    "/sharing_groups/edit/{sharingGroupId}",
    deprecated=True,
    response_model=partial(ViewUpdateSharingGroupLegacyResponse),
)
@with_session_management
async def update_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    body: UpdateSharingGroupLegacyBody,
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(404)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(404)

    update = body.dict(include={"name", "description", "releasability", "local", "active", "roaming"})
    update_record(sharing_group, update)

    db.commit()
    db.refresh(sharing_group)

    organisation = db.get(Organisation, sharing_group.org_id)
    sharing_group_orgs: list[SharingGroupOrg] = (
        db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id).all()
    )
    sharing_group_servers: list[SharingGroupServer] = (
        db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id).all()
    )

    sharing_group_orgs_computed: list[dict] = []

    for sharing_group_org in sharing_group_orgs:
        sharing_group_org_organisation: Organisation = db.get(Organisation, sharing_group_org.org_id)

        sharing_group_orgs_computed.append(
            {**sharing_group_org.__dict__, "Organisation": getattr(sharing_group_org_organisation, "__dict__", None)}
        )

    sharing_group_servers_computed: list[dict] = []

    for sharing_group_server in sharing_group_servers:
        if sharing_group_server.server_id == 0:
            sharing_group_server_server = LOCAL_INSTANCE_SERVER
        else:
            sharing_group_server_server = db.get(Server, sharing_group_server.server_id)
            sharing_group_server_server = getattr(sharing_group_server_server, "__dict__", None)

        sharing_group_servers_computed.append({**sharing_group_server.__dict__, "Server": sharing_group_server_server})

    return {
        "SharingGroup": sharing_group.__dict__,
        "Organisation": organisation.__dict__,
        "SharingGroupOrg": sharing_group_orgs_computed,
        "SharingGroupServer": sharing_group_servers_computed,
    }


@router.delete(
    "/sharing_groups/delete/{sharingGroupId}", deprecated=True, response_model=partial(DeleteSharingGroupLegacyResponse)
)
@with_session_management
async def delete_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group:
        raise HTTPException(404)

    sharing_group = cast(SharingGroup, sharing_group)

    if sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(404)

    db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == sharing_group.id).delete(False)
    db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == sharing_group.id).delete(False)

    db.delete(sharing_group)
    db.commit()

    return {
        "id": sharing_group.id,
        "saved": True,
        "success": True,
        "name": "Organisation removed from the sharing group.",
        "message": "Organisation removed from the sharing group.",
        "url": "/sharing_groups/removeOrg",
    }


@router.post(
    "/sharing_groups/addOrg/{sharingGroupId}/{organisationId}",
    deprecated=True,
    response_model=partial(StandardStatusResponse),
)
@with_session_management
async def add_org_to_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    organisation_id: Annotated[int, Path(alias="organisationId")],
    body: AddOrgToSharingGroupLegacyBody = AddOrgToSharingGroupLegacyBody(),
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_org: SharingGroupOrg | None = (
        db.query(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == organisation_id)
        .first()
    )

    if not sharing_group_org:
        sharing_group_org = SharingGroupOrg(
            sharing_group_id=id,
            org_id=organisation_id,
            extend=body.extend,
        )

        db.add(sharing_group_org)

    update_record(sharing_group_org, body.dict())

    db.commit()
    db.refresh(sharing_group_org)

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Organisation added to the sharing group.",
        message="Organisation added to the sharing group.",
        url="/sharing_groups/addOrg",
    )


@router.post(
    "/sharing_groups/removeOrg/{sharingGroupId}/{organisationId}",
    deprecated=True,
    response_model=partial(StandardStatusResponse),
)
@with_session_management
async def remove_org_from_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    organisation_id: Annotated[int, Path(alias="organisationId")],
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_org: SharingGroupOrg | None = (
        db.query(SharingGroupOrg)
        .filter(SharingGroupOrg.sharing_group_id == id, SharingGroupOrg.org_id == organisation_id)
        .first()
    )

    if not sharing_group_org:
        raise HTTPException(404)

    db.delete(sharing_group_org)
    db.commit()

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Organisation removed from the sharing group.",
        message="Organisation removed from the sharing group.",
        url="/sharing_groups/removeOrg",
    )


@router.post(
    "/sharing_groups/addServer/{sharingGroupId}/{serverId}",
    deprecated=True,
    response_model=partial(StandardStatusResponse),
)
@with_session_management
async def add_server_to_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    server_id: Annotated[int, Path(alias="serverId")],
    body: AddServerToSharingGroupLegacyBody = AddServerToSharingGroupLegacyBody(),
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_server: SharingGroupServer | None = (
        db.query(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == server_id)
        .first()
    )

    if not sharing_group_server:
        sharing_group_server = SharingGroupServer(
            sharing_group_id=id,
            server_id=server_id,
            all_orgs=body.all_orgs,
        )

        db.add(sharing_group_server)

    update_record(sharing_group_server, body.dict())

    db.commit()
    db.refresh(sharing_group_server)

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Server added to the sharing group.",
        message="Server added to the sharing group.",
        url="/sharing_groups/addServer",
    )


@router.post(
    "/sharing_groups/removeServer/{sharingGroupId}/{serverId}",
    deprecated=True,
    response_model=partial(StandardStatusResponse),
)
@with_session_management
async def remove_server_from_sharing_group_legacy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SHARING_GROUP]))],
    db: Annotated[Session, Depends(get_db)],
    id: Annotated[int, Path(alias="sharingGroupId")],
    server_id: Annotated[int, Path(alias="serverId")],
) -> dict:
    sharing_group: SharingGroup | None = db.get(SharingGroup, id)

    if not sharing_group or (
        sharing_group.org_id != auth.org_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(404)

    sharing_group_server: SharingGroupServer | None = (
        db.query(SharingGroupServer)
        .filter(SharingGroupServer.sharing_group_id == id, SharingGroupServer.server_id == server_id)
        .first()
    )

    if not sharing_group_server:
        raise HTTPException(404)

    db.delete(sharing_group_server)
    db.commit()

    return StandardStatusResponse(
        saved=True,
        success=True,
        name="Server removed from the sharing group.",
        message="Server removed from the sharing group.",
        url="/sharing_groups/removeServer",
    )
