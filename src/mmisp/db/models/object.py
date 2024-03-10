from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.db.database import Base
from mmisp.util.uuid import uuid


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    name = Column(String(255), index=True)
    meta_category = Column("meta-category", String(255), index=True, key="meta_category")
    description = Column(String(255))
    template_uuid = Column(String(255), index=True, default=None)
    template_version = Column(Integer, index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    timestamp = Column(Integer, index=True, nullable=False, default=0)
    distribution = Column(Integer, index=True, nullable=False, default=0)
    sharing_group_id = Column(Integer, ForeignKey("sharing_groups.id"), index=True)
    comment = Column(String(255), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    first_seen = Column(Integer, index=True, default=None)
    last_seen = Column(Integer, index=True, default=None)


class ObjectTemplate(Base):
    __tablename__ = "object_templates"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    name = Column(String(255), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id"), index=True, nullable=False)
    description = Column(String(255))
    version = Column(Integer, nullable=False)
    requirements = Column(String(255))
    fixed = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=False)
