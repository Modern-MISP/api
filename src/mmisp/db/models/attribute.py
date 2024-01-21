from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True)
    event_id = Column(String, ForeignKey("events.id"))
    object_id = Column(String, ForeignKey("objects.id"))
    object_relation = Column(String)
    category = Column(String)
    type = Column(String)
    value = Column(String)
    value1 = Column(String)
    value2 = Column(String)
    to_ids = Column(Boolean)
    uuid = Column(String)
    timestamp = Column(String)
    distribution = Column(String)
    sharing_group_id = Column(String, ForeignKey("sharing_groups.id"))
    comment = Column(String)
    deleted = Column(Boolean)
    disable_correlation = Column(Boolean)
    first_seen = Column(String)
    last_seen = Column(String)
    event_uuid = Column(String, ForeignKey("events.uuid"))  # new

    tags = relationship("AttributeTag")


class AttributeTag(Base):
    __talename__ = "attribute_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    colour = Column(String)
    exportable = Column(Boolean)
    user_id = Column(String)
    hide_tag = Column(Boolean)
    numerical_value = Column(Integer)
    is_galaxy = Column(Boolean)
    is_costum_galaxy = Column(Boolean)
    local_only = Column(Boolean)
