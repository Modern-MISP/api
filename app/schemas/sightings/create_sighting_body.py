from pydantic import BaseModel


class SightingCoreConfigBody(BaseModel):
    estimative_language_confidence_in_analytic_judgment: float
    estimative_language_likelihood_probability: float
    phishing_psychological_acceptability: float
    phishing_state: float


class SightingModelOverridesBody(BaseModel):
    lifetime: int
    decay_speed: float
    threshold: int
    default_base_score: int
    base_score_config: SightingCoreConfigBody


class SightingFiltersBody(BaseModel):
    page: int
    limit: int
    value: str
    value1: str
    value2: str
    type: str
    category: str
    org: str
    tags: list[str]
    from_: str  # 'from' is a reserved word in Python, so an underscore is added
    to: str
    last: int
    eventid: str
    withAttachments: bool
    uuid: str
    publish_timestamp: str
    published: bool
    timestamp: str
    attribute_timestamp: str
    enforceWarninglist: bool
    to_ids: bool
    deleted: bool
    event_timestamp: str
    threat_level_id: str
    eventinfo: str
    sharinggroup: list[str]
    decayingModel: str
    score: str
    first_seen: str
    last_seen: str
    includeEventUuid: bool
    includeEventTags: bool
    includeProposals: bool
    requested_attributes: list[str]
    includeContext: bool
    headerless: bool
    includeWarninglistHits: bool
    attackGalaxy: str
    object_relation: str
    includeSightings: bool
    includeCorrelations: bool
    modelOverrides: SightingModelOverridesBody
    includeDecayScore: bool
    includeFullModel: bool
    excludeDecayed: bool
    returnFormat: str


class SightingCreateBody(BaseModel):
    values: list[str]
    timestamp: str
    filters: SightingFiltersBody

    class Config:
        orm_mode = True
