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
    withAttachments: bool | None = None
    uuid: str | None = None
    publish_timestamp: str | None = None
    published: bool | None = None
    timestamp: str | None = None
    attribute_timestamp: str | None = None
    enforceWarninglist: bool | None = None
    to_ids: bool | None = None
    deleted: bool | None = None
    event_timestamp: str | None = None
    threat_level_id: str | None = None
    eventinfo: str | None = None
    sharinggroup: list[str] | None = None
    decayingModel: str | None = None
    score: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    includeEventUuid: bool | None = None
    includeEventTags: bool | None = None
    includeProposals: bool | None = None
    requested_attributes: list[str] | None = None
    includeContext: bool | None = None
    headerless: bool | None = None
    includeWarninglistHits: bool | None = None
    attackGalaxy: str | None = None
    object_relation: str | None = None
    includeSightings: bool | None = None
    includeCorrelations: bool | None = None
    modelOverrides: SearchAttributesModelOverrides | None = None
    includeDecayScore: bool | None = None
    includeFullModel: bool | None = None
    excludeDecayed: bool | None = None

    class Config:
        orm_mode = True
