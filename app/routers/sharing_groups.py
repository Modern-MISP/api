from fastapi import APIRouter

from app.schemas.sharing_groups.create_sharing_group_legacy_in import (
    CreateSharingGroupLegacyIn,
)
from app.schemas.sharing_groups.create_sharing_group_legacy_out import (
    CreateSharingGroupLegacyOut,
)
from app.schemas.sharing_groups.create_update_sharing_group_in import (
    CreateUpdateSharingGroupIn,
)
from app.schemas.sharing_groups.delete_sharing_group_legacy_out import (
    DeleteSharingGroupLegacyOut,
)
from app.schemas.sharing_groups.sharing_group import SharingGroup
from app.schemas.sharing_groups.update_sharing_group_legacy_in import (
    UpdateSharingGroupLegacyIn,
)
from app.schemas.sharing_groups.view_sharing_group_legacy_out import (
    ViewSharingGroupLegacyOut,
)
from app.schemas.sharing_groups.get_all_sharing_groups_out import GetAllSharingGroupsOut
from app.schemas.sharing_groups.get_sharing_group_info_out import GetSharingGroupInfoOut

router = APIRouter(tags=["sharing_groups"])


@router.post("/sharing_groups", status_code=201)
async def create_sharing_group(body: CreateUpdateSharingGroupIn) -> SharingGroup:
    return SharingGroup()


@router.get("/sharing_groups/{id}")
async def get_sharing_group(id: str) -> SharingGroup:
    return SharingGroup()


@router.put("/sharing_groups/{id}")
async def update_sharing_group(
    id: str, body: CreateUpdateSharingGroupIn
) -> SharingGroup:
    return SharingGroup()


@router.delete("/sharing_groups/{id}")
async def delete_sharing_group(id: str) -> SharingGroup:
    return SharingGroup()


@router.get("/sharing_groups")
async def get_all_sharing_groups() -> GetAllSharingGroupsOut:
    return None


@router.get("/sharing_groups/{id}/info")
async def get_sharing_group_info(id: str) -> GetSharingGroupInfoOut:
    return GetSharingGroupInfoOut()


# --- deprecated ---


@router.post("/sharing_groups/add", deprecated=True, status_code=201)
async def create_sharing_group_legacy(
    body: CreateSharingGroupLegacyIn,
) -> CreateSharingGroupLegacyOut:
    return CreateSharingGroupLegacyOut()


@router.get("/sharing_groups/view/{sharingGroupId}", deprecated=True)
async def view_sharing_group_legacy(sharingGroupId: str) -> ViewSharingGroupLegacyOut:
    return ViewSharingGroupLegacyOut()


@router.post("/sharing_groups/edit/{sharingGroupId}", deprecated=True)
async def update_sharing_group_legacy(
    sharingGroupId: str,
    body: UpdateSharingGroupLegacyIn,
) -> SharingGroup:
    return SharingGroup()


@router.delete("/sharing_groups/delete/{sharingGroupId}", deprecated=True)
async def delete_sharing_group_legacy(
    sharingGroupId: str,
) -> DeleteSharingGroupLegacyOut:
    return DeleteSharingGroupLegacyOut()
