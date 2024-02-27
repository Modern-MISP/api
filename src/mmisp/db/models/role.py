from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ..database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    created = Column(DateTime, default=None)
    modified = Column(DateTime, default=None)
    perm_add = Column(Boolean, default=False)
    perm_modify = Column(Boolean, default=False)
    perm_modify_org = Column(Boolean, default=False)
    perm_publish = Column(Boolean, default=False)
    perm_delegate = Column(Boolean, default=False)
    perm_sync = Column(Boolean, default=False)
    perm_admin = Column(Boolean, default=False)
    perm_audit = Column(Boolean, default=False)
    perm_full = Column(Boolean, default=False)
    perm_auth = Column(Boolean, default=False)
    perm_site_admin = Column(Boolean, default=False)
    perm_regexp_access = Column(Boolean, default=False)
    perm_tagger = Column(Boolean, default=False)
    perm_template = Column(Boolean, default=False)
    perm_sharing_group = Column(Boolean, default=False)
    perm_tag_editor = Column(Boolean, default=False)
    perm_sighting = Column(Boolean, default=False)
    perm_object_template = Column(Boolean, default=False)
    default_role = Column(Boolean, default=False)
    memory_limit = Column(String(255), default="")
    max_execution_time = Column(String(255), default="")
    restricted_to_site_admin = Column(Boolean, default=False)
    perm_publish_zmq = Column(Boolean, default=False)
    perm_publish_kafka = Column(Boolean, default=False)
    perm_decaying = Column(Boolean, default=False)
    enforce_rate_limit = Column(Boolean, default=False)
    rate_limit_count = Column(Integer, default=0)
