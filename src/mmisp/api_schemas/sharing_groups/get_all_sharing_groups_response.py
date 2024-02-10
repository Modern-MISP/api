from pydantic import BaseModel


class GetAllSharingGroupsResponseResponseItemSharingGroup(BaseModel):
    id: str
    uuid: str
    name: str
    description: str
    releasability: str
    local: bool
    active: bool
    roaming: bool
    org_count: str


class GetAllSharingGroupsResponseOrganisationInfo(BaseModel):
    id: str
    uuid: str
    name: str


class GetAllSharingGroupsResponseResponseItemSharingGroupOrgItem(BaseModel):
    id: str
    sharing_group_id: str
    org_id: str
    extend: bool
    Organisation: GetAllSharingGroupsResponseOrganisationInfo


class GetAllSharingGroupsResponseResponseItemSharingGroupServerItemServer(BaseModel):
    id: str
    name: str
    url: str


class GetAllSharingGroupsResponseResponseItemSharingGroupServerItem(BaseModel):
    server_id: str
    sharing_group_id: str
    all_orgs: bool
    Server: GetAllSharingGroupsResponseResponseItemSharingGroupServerItemServer


class GetAllSharingGroupsResponseResponseItem(BaseModel):
    SharingGroup: GetAllSharingGroupsResponseResponseItemSharingGroup
    Organisation: GetAllSharingGroupsResponseOrganisationInfo
    SharingGroupOrg: list[GetAllSharingGroupsResponseResponseItemSharingGroupOrgItem]
    SharingGroupServer: list[GetAllSharingGroupsResponseResponseItemSharingGroupServerItem]
    editable: bool
    deletable: bool


class GetAllSharingGroupsResponse(BaseModel):
    response: list[GetAllSharingGroupsResponseResponseItem]
