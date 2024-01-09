from .sharing_group import SharingGroup
from pydantic import BaseModel


class GetSharingGroupInfoOutSharingGroupInfo(SharingGroup):
    org_count: int
    user_count: int
    created_by_email: str


class GetSharingGroupInfoOutOrganisationInfo(BaseModel):
    id: str
    uuid: str
    name: str
    local: bool


class GetSharingGroupInfoOutSharingGroupOrgItem(BaseModel):
    id: str
    sharing_group_id: str
    org_id: str
    extend: bool
    Organisation: GetSharingGroupInfoOutOrganisationInfo


class GetSharingGroupInfoOutServerInfo(BaseModel):
    id: str
    name: str
    url: str


class GetSharingGroupInfoOutSharingGroupServerItem(BaseModel):
    id: str
    sharing_group_id: str
    server_id: str
    all_orgs: bool
    Server: GetSharingGroupInfoOutServerInfo


class GetSharingGroupInfoOut(BaseModel):
    SharingGroup: GetSharingGroupInfoOutSharingGroupInfo
    Organisation: None  # TODO link to org resource
    SharingGroupOrg: list[GetSharingGroupInfoOutSharingGroupOrgItem]
    SharingGroupServer: list[GetSharingGroupInfoOutSharingGroupServerItem]
