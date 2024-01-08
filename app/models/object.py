from sqlalchemy import Boolean, Column, String
from typing import List

from ..database import Base


class Attribute(Base):
    id = Column(String)
    event_id = Column(String)
    object_id = Column(String)
    object_relation = Column(String)
    category = Column(String)
    type = Column(String)
    value = Column(String)
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


class Object(Base):
    id = Column(String)
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
    Attribute: List[Attribute]


class Response(Base):
    Object: Object


class ObjectDelete(Base):
    saved = Column(String)
    success = Column(String)
    name = Column(String)
    message = Column(String)
    url = Column(String)
