from pydantic import BaseModel, Field

from .sharing_group import SharingGroup
from .sharing_group_server import SharingGroupServer


class CreateSharingGroupLegacyResponseOrganisationInfo(BaseModel):
    id: str
    name: str
    uuid: str


class CreateSharingGroupLegacyResponse(BaseModel):
    SharingGroup: SharingGroup
    Organisation: CreateSharingGroupLegacyResponseOrganisationInfo
    SharingGroupOrg: list = Field(default=[])
    SharingGroupServer: list[SharingGroupServer]
