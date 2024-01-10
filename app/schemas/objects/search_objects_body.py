from pydantic import BaseModel


class ModelSearchOverridesBody(BaseModel):
    lifetime: int
    decay_speed: float
    threshold: int
    default_base_score: int
    base_score_config: dict[str, float]


class ObjectSearchBody(BaseModel):
    page: int
    limit: int
    quickFilter: str
    searchall: str
    timestamp: str
    object_name: str
    object_template_uuid: str
    object_template_version: str
    eventid: str
    eventinfo: str
    ignore: bool
    from_: str  # 'from' is a reserved word in Python, so an underscore is added
    to: str
    date: str
    tags: list[str]
    last: int
    event_timestamp: str
    publish_timestamp: str
    org: str
    uuid: str
    value: str  # omitted
    value1: str  # new
    value2: str  # new
    type: str
    category: str
    object_relation: str
    attribute_timestamp: str
    first_seen: str
    last_seen: str
    comment: str
    to_ids: bool
    published: bool
    deleted: bool
    withAttachments: bool
    enforceWarninglist: bool
    includeAllTags: bool
    includeEventUuid: bool
    include_event_uuid: bool
    includeEventTags: bool
    includeProposals: bool
    includeWarninglistHits: bool
    includeContext: bool
    includeSightings: bool
    includeSightingdb: bool
    includeCorrelations: bool
    includeDecayScore: bool
    includeFullModel: bool
    allow_proposal_blocking: bool
    metadata: bool
    attackGalaxy: str
    excludeDecayed: bool
    decayingModel: str
    modelOverrides: ModelSearchOverridesBody
    score: str
    returnFormat: str

    class Config:
        orm_mode = True
        # allow_population_by_field_name = True
