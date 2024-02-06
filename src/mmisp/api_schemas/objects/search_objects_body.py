from pydantic import BaseModel


class ObjectModelSearchOverridesBody(BaseModel):
    lifetime: int | None = None
    decay_speed: float | None = None
    threshold: int | None = None
    default_base_score: int | None = None
    base_score_config: dict[str, float] | None = None


class ObjectSearchBody(BaseModel):
    # page: int | None = None
    # limit: int | None = None
    # quickFilter: str | None = None
    # searchall: str | None = None
    # timestamp: str | None = None
    name: str | None = None
    # template_uuid: str | None = None
    # template_version: str | None = None
    event_id: str | None = None
    # event_info: str | None = None
    # ignore: bool | None = None
    # from_: str | None = None  # ? 'from' is a reserved word in Python, so an underscore is added
    # to: str | None = None
    # date: str | None = None
    # tags: list[str] | None = None
    # last: int | None = None
    # event_timestamp: str | None = None
    # publish_timestamp: str | None = None
    # org: str | None = None
    # uuid: str | None = None
    # value: str | None = None  # depricated
    # value1: str | None = None  # new
    # value2: str | None = None  # new
    # type: str | None = None
    # category: str | None = None
    # object_relation: str | None = None
    # attribute_timestamp: str | None = None
    # first_seen: str | None = None
    # last_seen: str | None = None
    # comment: str | None = None
    # to_ids: bool | None = None
    # published: bool | None = None
    # deleted: bool | None = None
    # withAttachments: bool | None = None
    # enforceWarninglist: bool | None = None
    # includeAllTags: bool | None = None
    # includeEventUuid: bool | None = None
    # include_event_uuid: bool | None = None
    # includeEventTags: bool | None = None
    # includeProposals: bool | None = None
    # includeWarninglistHits: bool | None = None
    # includeContext: bool | None = None
    # includeSightings: bool | None = None
    # includeSightingdb: bool | None = None
    # includeCorrelations: bool | None = None
    # includeDecayScore: bool | None = None
    # includeFullModel: bool | None = None
    # allow_proposal_blocking: bool | None = None
    # metadata: bool | None = None
    # attackGalaxy: str | None = None
    # excludeDecayed: bool | None = None
    # decayingModel: str | None = None
    # modelOverrides: ObjectModelSearchOverridesBody | None = None
    # score: str | None = None
    # returnFormat: str | None = "json"

    class Config:
        orm_mode = True
