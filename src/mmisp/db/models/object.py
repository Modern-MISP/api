from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from mmisp.util.uuid import uuid

from ..database import Base


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    name = Column(String(255), index=True, nullable=False)
    object_relation = Column(String(255), index=True)
    meta_category = Column(String(255), index=True)
    description = Column(String(255))
    action = Column(String(255))
    template_id = Column(Integer, ForeignKey("object_templates.id"), index=True)
    template_name = Column(String(255), index=True)
    template_uuid = Column(String(255), index=True, default=None)
    template_version = Column(Integer, index=True, nullable=False, default=0)
    template_description = Column(String(255))
    update_template_available = Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    timestamp = Column(Integer, index=True, nullable=False, default=0)
    distribution = Column(Integer, index=True, nullable=False, default=0)
    sharing_group_id = Column(Integer, index=True)
    comment = Column(String(255), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    first_seen = Column(Integer, index=True, default=None)
    last_seen = Column(Integer, index=True, default=None)

    attributes = relationship("Attribute", backref="object")


class ObjectTemplate(Base):
    __tablename__ = "object_templates"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    name = Column(String(255), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id"), index=True, nullable=False)
    meta_category = Column(String(255), index=True)
    description = Column(String(255))
    version = Column(Integer, nullable=False)
    requirements = Column(String(255))
    fixed = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=False)
