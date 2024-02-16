from pydantic import BaseModel


class ExportGalaxyGalaxyElement(BaseModel):
    id: str | None = None
    galaxy_cluster_id: str | None = None
    key: str
    value: str


class ExportGalaxyResponse(BaseModel):
    id: str | None = None
    uuid: str | None = None
    collection_uuid: str
    type: str
    value: str
    tag_name: str
    description: str
    galaxy_id: str
    source: str
    authors: list[str]
    version: str
    distribution: str
    sharing_group_id: str
    org_id: str
    orgc_id: str
    default: bool
    locked: bool
    extends_uuid: str
    extends_version: str
    published: bool
    deleted: bool
    GalaxyElement: list[ExportGalaxyGalaxyElement]

    class Config:
        orm_mode = True
