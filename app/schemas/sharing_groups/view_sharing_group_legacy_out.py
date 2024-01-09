from .sharing_group import SharingGroup
from pydantic import BaseModel


class ViewSharingGroupLegacyOutOrganisationInfo(BaseModel):
    id: str
    uuid: str
    name: str
    local: bool


class ViewSharingGroupLegacyOutSharingGroupOrgItem(BaseModel):
    id: str
    sharing_group_id: str
    org_id: str
    extend: bool
    Organisation: ViewSharingGroupLegacyOutOrganisationInfo


class ViewSharingGroupLegacyOutServerInfo(BaseModel):
    id: str
    name: str
    url: str


class ViewSharingGroupLegacyOutSharingGroupServerItem(BaseModel):
    id: str
    sharing_group_id: str
    server_id: str
    all_orgs: bool
    Server: ViewSharingGroupLegacyOutServerInfo


class ViewSharingGroupLegacyOut(BaseModel):
    SharingGroup: SharingGroup
    Organisation: None  # TODO link to org resource
    SharingGroupOrg: list[ViewSharingGroupLegacyOutSharingGroupOrgItem]
    SharingGroupServer: list[ViewSharingGroupLegacyOutSharingGroupServerItem]
