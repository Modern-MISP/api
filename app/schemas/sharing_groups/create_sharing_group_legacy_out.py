from pydantic import Field
from pydantic import BaseModel

from .sharing_group import SharingGroup


class CreateSharingGroupLegacyOutOrganisationInfo(BaseModel):
    id: str
    name: str
    uuid: str


class CreateSharingGroupLegacyOutSharingGroupServerItem(BaseModel):
    id: str
    server_id: str
    all_orgs: bool
    sharing_group_id: str


class CreateSharingGroupLegacyOut(BaseModel):
    SharingGroup: SharingGroup
    Organisation: CreateSharingGroupLegacyOutOrganisationInfo
    SharingGroupOrg: list = Field(default=[])
    SharingGroupServer: list[CreateSharingGroupLegacyOutSharingGroupServerItem]
