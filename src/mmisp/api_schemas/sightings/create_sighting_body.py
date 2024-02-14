from pydantic import BaseModel


class SightingCoreConfigBody(BaseModel):
    estimative_language_confidence_in_analytic_judgment: str
    estimative_language_likelihood_probability: str
    phishing_psychological_acceptability: str
    phishing_state: str


class SightingModelOverridesBody(BaseModel):
    lifetime: str
    decay_speed: str
    threshold: str
    default_base_score: str
    base_score_config: SightingCoreConfigBody


class SightingFiltersBody(BaseModel):
    page: str
    limit: str
    value: str
    value1: str
    value2: str
    type: str
    category: str
    org: str
    tags: list[str]
    from_: str  # 'from' is a reserved word in Python, so an underscore is added
    to: str
    last: str
    event_id: str
    with_attachments: bool
    uuid: str
    publish_timestamp: str
    published: bool
    timestamp: str
    attribute_timestamp: str
    enforce_warninglist: bool
    to_ids: bool
    deleted: bool
    event_timestamp: str
    threat_level_id: str
    eventinfo: str
    sharinggroup: list[str]
    decaying_model: str
    score: str
    first_seen: str
    last_seen: str
    include_event_uuid: bool
    include_event_tags: bool
    include_proposals: bool
    requested_attributes: list[str]
    include_context: bool
    headerless: bool
    include_warninglist_hits: bool
    attack_galaxy: str
    object_relation: str
    include_sightings: bool
    include_correlations: bool
    model_overrides: SightingModelOverridesBody
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
