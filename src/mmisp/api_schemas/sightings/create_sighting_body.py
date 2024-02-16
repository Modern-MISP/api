from pydantic import BaseModel


class SightingCoreConfigBody(BaseModel):
    estimative_language_confidence_in_analytic_judgment: str | None = None
    estimative_language_likelihood_probability: str | None = None
    phishing_psychological_acceptability: str | None = None
    phishing_state: str | None = None


class SightingModelOverridesBody(BaseModel):
    lifetime: str | None = None
    decay_speed: str | None = None
    threshold: str | None = None
    default_base_score: str | None = None
    base_score_config: SightingCoreConfigBody | None = None


class SightingFiltersBody(BaseModel):
    page: str | None = None
    limit: str | None = None
    value: str | None = None
    value1: str | None = None
    value2: str | None = None
    type: str | None = None
    category: str | None = None
    org_id: str | None = None
    tags: list[str] | None = None
    from_: str | None = None  # 'from' is a reserved word in Python, so an underscore is added
    to: str | None = None
    last: str | None = None
    event_id: str | None = None
    with_attachments: bool | None = None
    uuid: str | None = None
    publish_timestamp: str | None = None
    published: bool | None = None
    timestamp: str | None = None
    attribute_timestamp: str | None = None
    enforce_warninglist: bool | None = None
    to_ids: bool | None = None
    deleted: bool | None = None
    event_timestamp: str | None = None
    threat_level_id: str | None = None
    eventinfo: str | None = None
    sharinggroup: list[str] | None = None
    decaying_model: str | None = None
    score: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    include_event_uuid: bool | None = None
    include_event_tags: bool | None = None
    include_proposals: bool | None = None
    requested_attributes: list[str]
    include_context: bool | None = None
    headerless: bool | None = None
    include_warninglist_hits: bool | None = None
    attack_galaxy: str | None = None
    object_relation: str | None = None
    include_sightings: bool | None = None
    include_correlations: bool | None = None
    model_overrides: SightingModelOverridesBody | None = None
    includeDecayScore: bool | None = None
    includeFullModel: bool | None = None
    excludeDecayed: bool | None = None
    returnFormat: str | None = "json"


class SightingCreateBody(BaseModel):
    values: list[str]
    source: str | None = None
    timestamp: str | None = None
    filters: SightingFiltersBody | None = None

    class Config:
        orm_mode = True
