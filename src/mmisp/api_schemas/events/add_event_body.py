from pydantic import BaseModel

#  from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody


class AddEventTag(BaseModel):
    name: str


class AddEventBody(BaseModel):
    info: str
    org_id: str | None = None
    distribution: str | None = None
    orgc_id: str | None = None
    uuid: str | None = None
    date: str | None = None
    published: bool | None = None
    analysis: str | None = None
    attribute_count: str | None = None
    timestamp: str | None = None
    sharing_group_id: str | None = None
    proposal_email_lock: bool | None = None
    locked: bool | None = None
    threat_level_id: str | None = None
    publish_timestamp: str | None = None
    sighting_timestamp: str | None = None
    disable_correlation: bool | None = None
    extends_uuid: str | None = None
    event_creator_email: str | None = None
    protected: str | None = None
    cryptographic_key: str | None = None
    # Attribute: list[AddAttributeBody] | None = None
    # Tag: list[AddEventTag] | None = None

    class Config:
        orm_mode = True