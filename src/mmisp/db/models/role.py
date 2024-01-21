from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import TINYINT

from ..database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime)
    modified = Column(DateTime)
    perm_add = Column(TINYINT)
    perm_modify = Column(TINYINT)
    perm_modify_org = Column(TINYINT)
    perm_publish = Column(TINYINT)
    perm_delegate = Column(TINYINT)
    perm_sync = Column(TINYINT)
    perm_admin = Column(TINYINT)
    perm_audit = Column(TINYINT)
    perm_full = Column(TINYINT)
    perm_auth = Column(TINYINT)
    perm_site_admin = Column(TINYINT)
    perm_regexp_access = Column(TINYINT)
    perm_tagger = Column(TINYINT)
    perm_template = Column(TINYINT)
    perm_sharing_group = Column(TINYINT)
    perm_tag_editor = Column(TINYINT)
    perm_sighting = Column(TINYINT)
    perm_object_template = Column(TINYINT)
    default_role = Column(TINYINT)
    memory_limit = Column(String)
    max_execution_time = Column(String)
    restricted_to_site_admin = Column(TINYINT)
    perm_publish_zmq = Column(TINYINT)
    perm_publish_kafka = Column(TINYINT)
    perm_decaying = Column(TINYINT)
    enforce_rate_limit = Column(TINYINT)
    rate_limit_count = Column(Integer)
    perm_galaxy_editor = Column(TINYINT)
    perm_warninglist = Column(TINYINT)
    perm_view_feed_correlations = Column(TINYINT)
