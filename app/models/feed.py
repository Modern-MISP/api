from sqlalchemy import Column, String, Boolean, Integer
from ..database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    provider = Column(String)
    url = Column(String)
    rules = Column(String)
    enabled = Column(Boolean)
    distribution = Column(String)
    sharing_group_id = Column(String)
    tag_id = Column(String)
    default = Column(Boolean)
    source_format = Column(String)
    fixed_event = Column(Boolean)
    delta_merge = Column(Boolean)
    event_id = Column(String)
    publish = Column(Boolean)
    override_ids = Column(Boolean)
    settings = Column(String)
    input_source = Column(String)
    delete_local_file = Column(Boolean)
    lookup_visible = Column(Boolean)
    headers = Column(String)
    caching_enabled = Column(Boolean)
    force_to_ids = Column(Boolean)
    orgc_id = Column(String)
    cache_timestamp = Column(String)
    cached_elements = Column(Integer)  # new
    coverage_by_other_feeds = Column(String)  # new
