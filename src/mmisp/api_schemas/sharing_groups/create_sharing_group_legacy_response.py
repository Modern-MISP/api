from pydantic import BaseModel

from .sharing_group import SharingGroup
from .sharing_group_org import SharingGroupOrg
from .sharing_group_server import SharingGroupServer


class CreateSharingGroupLegacyResponseOrganisationInfo(BaseModel):
    id: str
    name: str
    uuid: str


class CreateSharingGroupLegacyResponse(BaseModel):
    SharingGroup: SharingGroup
    Organisation: CreateSharingGroupLegacyResponseOrganisationInfo
    SharingGroupOrg: list[SharingGroupOrg]
    SharingGroupServer: list[SharingGroupServer]
