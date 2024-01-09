from pydantic import BaseModel


class GetAllSharingGroupOutResponseItemSharingGroup(BaseModel):
    id: str
    uuid: str
    name: str
    description: str
    releasability: str
    local: bool
    active: bool
    roaming: bool
    org_count: str


class GetAllSharingGroupOutOrganisationInfo(BaseModel):
    id: str
    uuid: str
    name: str


class GetAllSharingGroupOutResponseItemSharingGroupOrgItem(BaseModel):
    id: str
    sharing_group_id: str
    org_id: str
    extend: bool
    Organisation: GetAllSharingGroupOutOrganisationInfo


class GetAllSharingGroupOutResponseItemSharingGroupServerItem(BaseModel):
    server_id: str
    sharing_group_id: str
    all_orgs: bool
    Server: list = []


class GetAllSharingGroupOutResponseItem(BaseModel):
    SharingGroup: GetAllSharingGroupOutResponseItemSharingGroup
    Organisation: GetAllSharingGroupOutOrganisationInfo
    SharingGroupOrg: list[GetAllSharingGroupOutResponseItemSharingGroupOrgItem]
    SharingGroupServer: list[GetAllSharingGroupOutResponseItemSharingGroupServerItem]
    editable: bool
    deletable: bool


class GetAllSharingGroupsOut(BaseModel):
    response: list[GetAllSharingGroupOutResponseItem]
