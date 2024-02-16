from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ..database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    perm_add = Column(Boolean)
    perm_modify = Column(Boolean)
    perm_modify_org = Column(Boolean)
    perm_publish = Column(Boolean)
    perm_delegate = Column(Boolean)
    perm_sync = Column(Boolean)
    perm_admin = Column(Boolean)
    perm_audit = Column(Boolean)
    perm_full = Column(Boolean)
    """deprecated"""
    perm_auth = Column(Boolean)
    perm_site_admin = Column(Boolean)
    perm_regexp_access = Column(Boolean)
    perm_tagger = Column(Boolean)
    perm_template = Column(Boolean)
    perm_sharing_group = Column(Boolean)
    perm_tag_editor = Column(Boolean)
    perm_sighting = Column(Boolean)
    perm_object_template = Column(Boolean)
    default_role = Column(Boolean)
    memory_limit = Column(String(255))
    max_execution_time = Column(String(255))
    restricted_to_site_admin = Column(Boolean)
    perm_publish_zmq = Column(Boolean)
    perm_publish_kafka = Column(Boolean)
    perm_decaying = Column(Boolean)
    enforce_rate_limit = Column(Boolean)
    rate_limit_count = Column(Integer)
    perm_galaxy_editor = Column(Boolean)
    perm_warninglist = Column(Boolean)
    perm_view_feed_correlations = Column(Boolean)
