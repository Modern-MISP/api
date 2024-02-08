from sqlalchemy import Boolean, Column, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    rules = Column(String(255), nullable=True)
    enabled = Column(Boolean, default=False)
    distribution = Column(Integer, default=0, nullable=False)
    sharing_group_id = Column(Integer, default=0, nullable=False)
    tag_id = Column(Integer, default=0, nullable=False)
    default = Column(Boolean, default=False)
    source_format = Column(String(255), default="misp")
    fixed_event = Column(Boolean, default=False, nullable=False)
    delta_merge = Column(Boolean, default=False, nullable=False)
    event_id = Column(Integer, default=0, nullable=False)
    publish = Column(Boolean, default=False, nullable=False)
    override_ids = Column(Boolean, default=False, nullable=False)
    settings = Column(String(255), nullable=True)
    input_source = Column(String(255), index=True, default="network", nullable=False)
    delete_local_file = Column(Boolean, default=False)
    lookup_visible = Column(Boolean, default=False)
    headers = Column(String(255), nullable=True)
    caching_enabled = Column(Boolean, default=False, nullable=False)
    force_to_ids = Column(Boolean, default=False, nullable=False)
    orgc_id = Column(Integer, index=True, default=0, nullable=False)
    cache_timestamp = Column(String(255), nullable=True)
    cached_elements = Column(String(255), nullable=True)  # new
    coverage_by_other_feeds = Column(String(255), nullable=True)  # new
