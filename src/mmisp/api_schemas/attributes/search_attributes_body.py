from typing import Annotated

from pydantic import BaseModel, Field


class SearchAttributesModelOverridesBaseScoreConfig(BaseModel):
    estimative_language_confidence_in_analytic_judgment: Annotated[
        int, Field(alias="estimative-language:confidence-in-analytic-judgment")
    ]
    estimative_language_likelihood_probability: Annotated[
        int, Field(alias="estimative-language:likelihood-probability")
    ]
    phishing_psychological_acceptability: Annotated[int, Field(alias="phishing:psychological-acceptability")]
    phishing_state: Annotated[int, Field(alias="phishing:state")]


class SearchAttributesModelOverrides(BaseModel):
    lifetime: int
    decay_speed: int
    threshold: int
    default_base_score: int
    base_score_config: SearchAttributesModelOverridesBaseScoreConfig


class SearchAttributesBody(BaseModel):
    # return_format: Annotated[str, Field(alias="returnFormat")]
    returnFormat: str
    page: int | None = None
    limit: int | None = None
    value: str | None = None
    value1: str | None = None
    value2: str | None = None
    type: str | None = None
    category: str | None = None
    org: str | None = None
    tags: list[str] | None = None
    from_: str | None = None
    to: str | None = None
    last: int | None = None
    eventid: str | None = None
    with_attachments: Annotated[bool | None, Field(alias="withAttachments")] = None
    uuid: str | None = None
    publish_timestamp: str | None = None
    published: bool | None = None
    timestamp: str | None = None
    attribute_timestamp: str | None = None
    enforce_warninglist: Annotated[bool | None, Field(alias="enforceWarninglist")]
    to_ids: bool | None = None
    deleted: bool | None = None
    event_timestamp: str | None = None
    threat_level_id: str | None = None
    eventinfo: str | None = None
    sharinggroup: list[str] | None = None
    decaying_model: Annotated[str | None, Field(alias="decayingModel")] = None
    score: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    include_event_uuid: Annotated[bool | None, Field(alias="includeEventUuid")] = None
    include_event_tags: Annotated[bool | None, Field(alias="includeEventTags")] = None
    include_proposals: Annotated[bool | None, Field(alias="includeProposals")] = None
    requested_attributes: list[str] | None = None
    include_context: Annotated[bool | None, Field(alias="includeContext")] = None
    headerless: bool | None = None
    include_warninglist_hits: Annotated[bool | None, Field(alias="includeWarninglistHits")] = None
    attack_galaxy: Annotated[str | None, Field(alias="attackGalaxy")] = None
    object_relation: str | None = None
    include_sightings: Annotated[bool | None, Field(alias="includeSightings")] = None
    include_correlations: Annotated[bool | None, Field(alias="includeCorrelations")] = None
    model_overrides: Annotated[SearchAttributesModelOverrides | None, Field(alias="modelOverrides")] = None
    include_decay_score: Annotated[bool | None, Field(alias="includeDecayScore")] = None
    include_full_model: Annotated[bool | None, Field(alias="includeFullModel")] = None
    exclude_decayed: Annotated[bool | None, Field(alias="excludeDecayed")] = None

    class Config:
        orm_mode = True
