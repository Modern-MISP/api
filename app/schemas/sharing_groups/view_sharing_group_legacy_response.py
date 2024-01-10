from .sharing_group import SharingGroup
from pydantic import BaseModel


class ViewSharingGroupLegacyResponseOrganisationInfo(BaseModel):
    id: str
    uuid: str
    name: str
    local: bool


class ViewSharingGroupLegacyResponseSharingGroupOrgItem(BaseModel):
    id: str
    sharing_group_id: str
    org_id: str
    extend: bool
    Organisation: ViewSharingGroupLegacyResponseOrganisationInfo


class ViewSharingGroupLegacyResponseServerInfo(BaseModel):
    id: str
    name: str
    url: str


class ViewSharingGroupLegacyResponseSharingGroupServerItem(BaseModel):
    id: str
    sharing_group_id: str
    server_id: str
    all_orgs: bool
    Server: ViewSharingGroupLegacyResponseServerInfo


class ViewSharingGroupLegacyResponse(BaseModel):
    SharingGroup: SharingGroup
    Organisation: None  # TODO link to org resource
    SharingGroupOrg: list[ViewSharingGroupLegacyResponseSharingGroupOrgItem]
    SharingGroupServer: list[ViewSharingGroupLegacyResponseSharingGroupServerItem]
