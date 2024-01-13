from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TINYINT
from ..database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    provider = Column(String)
    url = Column(String)
    rules = Column(String)
    enabled = Column(TINYINT)
    distribution = Column(String)
    sharing_group_id = Column(String)
    tag_id = Column(String)
    default = Column(TINYINT)
    source_format = Column(String)
    fixed_event = Column(TINYINT)
    delta_merge = Column(TINYINT)
    event_id = Column(String)
    publish = Column(TINYINT)
    override_ids = Column(TINYINT)
    settings = Column(String)
    input_source = Column(String)
    delete_local_file = Column(TINYINT)
    lookup_visible = Column(TINYINT)
    headers = Column(String)
    caching_enabled = Column(TINYINT)
    force_to_ids = Column(TINYINT)
    orgc_id = Column(String)
    cache_timestamp = Column(String)
    cached_elements = Column(Integer)  # new
    coverage_by_other_feeds = Column(String)  # new
