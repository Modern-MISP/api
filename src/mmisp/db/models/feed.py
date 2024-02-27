from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.db.database import Base

# from mmisp.util.uuid import uuid


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    rules = Column(String(255), default=None)
    enabled = Column(Boolean, default=False)
    distribution = Column(Integer, nullable=False, default=0)
    sharing_group_id = Column(Integer, ForeignKey("sharing_groups.id"), index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    default = Column(Boolean, default=False)
    source_format = Column(String(255), default="misp")
    fixed_event = Column(Boolean, nullable=False, default=False)
    delta_merge = Column(Boolean, nullable=False, default=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    publish = Column(Boolean, nullable=False, default=False)
    override_ids = Column(Boolean, nullable=False, default=False)
    settings = Column(String(255))
    input_source = Column(String(255), index=True, nullable=False, default="network")
    delete_local_file = Column(Boolean, default=False)
    lookup_visible = Column(Boolean, default=False)
    headers = Column(String(255))
    caching_enabled = Column(Boolean, nullable=False, default=False)
    force_to_ids = Column(Boolean, nullable=False, default=False)
    orgc_id = Column(Integer, index=True, nullable=False, default=0)
