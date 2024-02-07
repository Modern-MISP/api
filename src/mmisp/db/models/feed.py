from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    rules = Column(String(255), nullable=True)
    enabled = Column(Boolean, default=False)
    distribution = Column(Integer, default=0)
    sharing_group_id = Column(Integer, default=0)
    tag_id = Column(Integer, default=0)
    default = Column(Boolean, default=False)
    source_format = Column(String(255), default="misp")
    fixed_event = Column(Boolean, default=False)
    delta_merge = Column(Boolean, default=False)
    event_id = Column(Integer, default=0)
    publish = Column(Boolean, default=False)
    override_ids = Column(Boolean, default=False)
    settings = Column(String(255), nullable=True)
    input_source = Column(String(255), index=True, default="network")
    delete_local_file = Column(Boolean, default=False)
    lookup_visible = Column(Boolean, default=False)
    headers = Column(String(255), nullable=True)
    caching_enabled = Column(Boolean, default=False)
    force_to_ids = Column(Boolean, default=False)
    orgc_id = Column(Integer, index=True, default=0)
    cache_timestamp = Column(String(255), nullable=True)
    cached_elements = Column(String(255), nullable=True)  # new
    coverage_by_other_feeds = Column(String(255), nullable=True)  # new
