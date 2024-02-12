from pydantic import BaseModel

from ..organisations.organisation import Organisation
from .sharing_group import SharingGroup


class ViewUpdateSharingGroupLegacyResponseOrganisationInfo(BaseModel):
    id: str
    uuid: str
    name: str
    local: bool


class ViewUpdateSharingGroupLegacyResponseSharingGroupOrgItem(BaseModel):
    id: str
    sharing_group_id: str
    org_id: str
    extend: bool
    Organisation: ViewUpdateSharingGroupLegacyResponseOrganisationInfo


class ViewUpdateSharingGroupLegacyResponseServerInfo(BaseModel):
    id: str
    name: str
    url: str


class ViewUpdateSharingGroupLegacyResponseSharingGroupServerItem(BaseModel):
    id: str
    sharing_group_id: str
    server_id: str
    all_orgs: bool
    Server: ViewUpdateSharingGroupLegacyResponseServerInfo


class ViewUpdateSharingGroupLegacyResponse(BaseModel):
    SharingGroup: SharingGroup
    Organisation: Organisation
    SharingGroupOrg: list[ViewUpdateSharingGroupLegacyResponseSharingGroupOrgItem]
    SharingGroupServer: list[ViewUpdateSharingGroupLegacyResponseSharingGroupServerItem]
