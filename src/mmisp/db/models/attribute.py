from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from .event import Event
from .object import Object
from .sharing_group import SharingGroup
from ..database import Base


class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.id))
    object_id = Column(Integer, ForeignKey(Object.id))
    object_relation = Column(String(255))
    category = Column(String(255))
    type = Column(String(255))
    value = Column(String(255))
    value1 = Column(String(255))
    value2 = Column(String(255))
    to_ids = Column(Boolean)
    uuid = Column(String(255))
    timestamp = Column(String(255))
    distribution = Column(String(255))
    sharing_group_id = Column(Integer, ForeignKey(SharingGroup.id))
    comment = Column(String(255))
    deleted = Column(Boolean)
    disable_correlation = Column(Boolean)
    first_seen = Column(String(255))
    last_seen = Column(String(255))
    event_uuid = Column(String(255), ForeignKey(Event.uuid))  # new

    # tags = relationship("AttributeTag")


class AttributeTag(Base):
    __tablename__ = "attribute_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    colour = Column(String(255))
    exportable = Column(Boolean)
    user_id = Column(String(255))
    hide_tag = Column(Boolean)
    numerical_value = Column(Integer)
    is_galaxy = Column(Boolean)
    is_costum_galaxy = Column(Boolean)
    local_only = Column(Boolean)
