from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from mmisp.util.uuid import uuid

from ..database import Base


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255), index=True)
    description = Column(String(255))
    template_id = Column(Integer, ForeignKey("object_templates.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    meta_category = Column(String(255), index=True)
    distribution = Column(Integer, index=True)
    deleted = Column(Boolean)
    sharing_group_id = Column(Integer, index=True)
    comment = Column(String(255))
    first_seen = Column(String(255), index=True)
    last_seen = Column(String(255), index=True)

    attributes = relationship("Attribute", backref="attribute")


class ObjectTemplate(Base):
    __tablename__ = "object_templates"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255))
    version = Column(String(255))
    description = Column(String(255))
    meta_category = Column(String(255))
