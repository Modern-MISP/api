from pydantic import Field
from pydantic import BaseModel

from .sharing_group import SharingGroup


class CreateSharingGroupLegacyResponseOrganisationInfo(BaseModel):
    id: str
    name: str
    uuid: str


class CreateSharingGroupLegacyResponseSharingGroupServerItem(BaseModel):
    id: str
    server_id: str
    all_orgs: bool
    sharing_group_id: str


class CreateSharingGroupLegacyResponse(BaseModel):
    SharingGroup: SharingGroup
    Organisation: CreateSharingGroupLegacyResponseOrganisationInfo
    SharingGroupOrg: list = Field(default=[])
    SharingGroupServer: list[CreateSharingGroupLegacyResponseSharingGroupServerItem]
