from sqlalchemy import Boolean, Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..database import Base


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    meta_category = Column(String)
    description = Column(String)
    template_uuid = Column(String)
    template_version = Column(String)
    event_id = Column(String)
    uuid = Column(String)
    timestamp = Column(String)
    distribution = Column(String)
    sharing_group_id = Column(String)
    comment = Column(String)
    deleted = Column(Boolean)
    first_seen = Column(String)
    last_seen = Column(String)

    attributes = relationship("ObjectAttribute", backref="object")


class ObjectAttribute(Base):
    __tablename__ = "object_attributes"

    id = Column(Integer, primary_key=True)
    event_id = Column(String)
    object_id = Column(String, ForeignKey("objects.id"))
    object_relation = Column(String)
    category = Column(String)
    type = Column(String)
    value1 = Column(String)
    value2 = Column(String)
    attribute_tag = Column(String)
    to_ids = Column(Boolean)
    uuid = Column(String)
    timestamp = Column(String)
    distribution = Column(String)
    sharing_group_id = Column(String)
    comment = Column(String)
    deleted = Column(Boolean)
    disable_correlation = Column(Boolean)
    first_seen = Column(String)
    last_seen = Column(String)
