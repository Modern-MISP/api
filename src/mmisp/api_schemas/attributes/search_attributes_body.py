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
    page: int
    limit: int
    value: str
    value1: str
    value2: str
    type: str
    category: str
    org: str
    tags: list[str]
    from_: str
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
    modelOverrides: SearchAttributesModelOverrides
    includeDecayScore: bool
    includeFullModel: bool
    excludeDecayed: bool

    class Config:
        orm_mode = True
