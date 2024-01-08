from typing import List

from sqlalchemy import Boolean, Column, String

from ..database import Base


class Attribute(Base):
    __tablename__ = "attributes"
    id = Column(String)
    event_id = Column(String)
    object_id = Column(String)
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
    sharing_group_id = Column(String)
    comment = Column(String)
    deleted = Column(Boolean)
    disable_correlation = Column(Boolean)
    first_seen = Column(String)
    last_seen = Column(String)
    event_uuid = Column(String)
    attributeTag = Column(List[String])


class ShadowAttribute(Base):
    value = Column(String)
    to_ids = Column(Boolean)
    type = Column(String)
    category = Column(String)
