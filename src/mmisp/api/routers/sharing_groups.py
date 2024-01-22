from fastapi import APIRouter, Depends

from mmisp.api_schemas.sharing_groups.add_org_to_sharing_group_body import (
    AddOrgToSharingGroupBody,
)
from mmisp.api_schemas.sharing_groups.add_org_to_sharing_group_legacy_body import (
    AddOrgToSharingGroupLegacyBody,
)
from mmisp.api_schemas.sharing_groups.add_server_to_sharing_group_body import (
    AddServerToSharingGroupBody,
)
from mmisp.api_schemas.sharing_groups.add_server_to_sharing_group_legacy_body import (
    AddServerToSharingGroupLegacyBody,
)
from mmisp.api_schemas.sharing_groups.create_sharing_group_legacy_body import (
    CreateSharingGroupLegacyBody,
)
from mmisp.api_schemas.sharing_groups.create_sharing_group_legacy_response import (
    CreateSharingGroupLegacyResponse,
)
from mmisp.api_schemas.sharing_groups.create_update_sharing_group_body import (
    CreateUpdateSharingGroupBody,
)
from mmisp.api_schemas.sharing_groups.delete_sharing_group_legacy_response import (
    DeleteSharingGroupLegacyResponse,
)
from mmisp.api_schemas.sharing_groups.get_all_sharing_groups_response import (
    GetAllSharingGroupsResponse,
)
from mmisp.api_schemas.sharing_groups.get_sharing_group_info_response import (
    GetSharingGroupInfoResponse,
)
from mmisp.api_schemas.sharing_groups.sharing_group import SharingGroup
from mmisp.api_schemas.sharing_groups.sharing_group_org import SharingGroupOrg
from mmisp.api_schemas.sharing_groups.sharing_group_server import SharingGroupServer
from mmisp.api_schemas.sharing_groups.update_sharing_group_legacy_body import (
    UpdateSharingGroupLegacyBody,
)
from mmisp.api_schemas.sharing_groups.view_sharing_group_legacy_response import (
    ViewSharingGroupLegacyResponse,
)
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from typing import Annotated
from sqlalchemy.orm import Session
from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.db.database import get_db

router = APIRouter(tags=["sharing_groups"])


@router.post("/sharing_groups", status_code=201)
async def create_sharing_group(
    auth: Annotated[
        Auth,
        Depends(
            authorize(AuthStrategy.ALL, [Permission.ADD, Permission.SHARING_GROUP])
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
    body: CreateUpdateSharingGroupBody,
) -> SharingGroup:
    return SharingGroup()


@router.get("/sharing_groups/{id}")
async def get_sharing_group(
    auth: Annotated[
        Auth,
        Depends(authorize(AuthStrategy.ALL, [Permission.SHARING_GROUP])),
    ],
    db: Annotated[Session, Depends(get_db)],
    id: str,
) -> SharingGroup:
    return SharingGroup()


@router.put("/sharing_groups/{id}")
async def update_sharing_group(
    auth: Annotated[
        Auth,
        Depends(
            authorize(AuthStrategy.ALL, [Permission.MODIFY, Permission.SHARING_GROUP])
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
    id: str,
    body: CreateUpdateSharingGroupBody,
) -> SharingGroup:
    return SharingGroup()


@router.delete("/sharing_groups/{id}")
async def delete_sharing_group(
    auth: Annotated[
        Auth,
        Depends(
            authorize(AuthStrategy.ALL, [Permission.MODIFY, Permission.SHARING_GROUP])
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
    id: str,
) -> SharingGroup:
    return SharingGroup()


@router.get("/sharing_groups")
async def get_all_sharing_groups() -> GetAllSharingGroupsResponse:
    return None


@router.get("/sharing_groups/{id}/info")
async def get_sharing_group_info(id: str) -> GetSharingGroupInfoResponse:
    return GetSharingGroupInfoResponse()


@router.patch("/sharing_groups/{id}/organizations")
async def add_org_to_sharing_group(
    id: str,
    body: AddOrgToSharingGroupBody,
) -> SharingGroupOrg:
    return SharingGroupOrg()


@router.delete("/sharing_groups/{id}/organizations/{organisationId}")
async def remove_org_from_sharing_group(
    id: str,
    organisationId: str,
) -> SharingGroupOrg:
    return SharingGroupOrg()


@router.patch("/sharing_groups/{id}/servers")
async def add_server_to_sharing_group(
    id: str,
    body: AddServerToSharingGroupBody,
) -> SharingGroupServer:
    return SharingGroupServer()


@router.delete("/sharing_groups/{id}/servers/{serverId}")
async def remove_server_from_sharing_group(
    id: str,
    serverId: str,
) -> SharingGroupServer:
    return SharingGroupServer()


# --- deprecated ---


@router.post("/sharing_groups/add", deprecated=True, status_code=201)
async def create_sharing_group_legacy(
    body: CreateSharingGroupLegacyBody,
) -> CreateSharingGroupLegacyResponse:
    return CreateSharingGroupLegacyResponse()


@router.get("/sharing_groups/view/{sharingGroupId}", deprecated=True)
async def view_sharing_group_legacy(
    sharingGroupId: str,
) -> ViewSharingGroupLegacyResponse:
    return ViewSharingGroupLegacyResponse()


@router.post("/sharing_groups/edit/{sharingGroupId}", deprecated=True)
async def update_sharing_group_legacy(
    sharingGroupId: str,
    body: UpdateSharingGroupLegacyBody,
) -> SharingGroup:
    return SharingGroup()


@router.delete("/sharing_groups/delete/{sharingGroupId}", deprecated=True)
async def delete_sharing_group_legacy(
    sharingGroupId: str,
) -> DeleteSharingGroupLegacyResponse:
    return DeleteSharingGroupLegacyResponse()


@router.post(
    "/sharing_groups/addOrg/{sharingGroupId}/{organisationId}",
    deprecated=True,
)
async def add_org_to_sharing_group_legacy(
    sharingGroupId: str,
    organisationId: str,
    body: AddOrgToSharingGroupLegacyBody,
) -> StandardStatusResponse:
    return StandardStatusResponse()


@router.post(
    "/sharing_groups/removeOrg/{sharingGroupId}/{organisationId}",
    deprecated=True,
)
async def remove_org_from_sharing_group_legacy(
    sharingGroupId: str,
    organisationId: str,
) -> StandardStatusResponse:
    return StandardStatusResponse()


@router.post(
    "/sharing_groups/addServer/{sharingGroupId}/{serverId}",
    deprecated=True,
)
async def add_server_to_sharing_group_legacy(
    sharingGroupId: str,
    serverId: str,
    body: AddServerToSharingGroupLegacyBody,
) -> StandardStatusResponse:
    return StandardStatusResponse()


@router.post(
    "/sharing_groups/removeServer/{sharingGroupId}/{serverId}",
    deprecated=True,
)
async def remove_server_from_sharing_group_legacy(
    sharingGroupId: str,
    serverId: str,
) -> StandardStatusResponse:
    return StandardStatusResponse()
