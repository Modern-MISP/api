from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Feed(Base):
    __tablename__ = "feeds"
    id = Column(String, primary_key=True)
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
    cache_timestamp = Column(String)  # is sometimes omitted, but is always implemented


class FeedView(Base):
    __tablename__ = "view_feeds"
    id = Column(String, primary_key=True)
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
    cache_timestamp = Column(String)  # omitted
    cached_elements = Column(Integer)  # new
    coverage_by_other_feeds = Column(String)  # new


class FeedTogle(Base):
    __tablename__ = "togle_feeds"
    name = Column(String, primary_key=True)
    message = Column(String)
    url = Column(String)


class FeedCache(Base):
    __tablename__ = "cache_feeds"
    name = Column(String, primary_key=True)
    message = Column(String)
    url = Column(String)
    saved = Column(Boolean)  # new
    success = Column(Boolean)  # new


class FeedFetch(Base):
    __tablename__ = "fetch_feeds"
    result = Column(String, primary_key=True)
