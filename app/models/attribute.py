from sqlalchemy import Boolean, Column, String
from sqlalchemy import ForeignKey

from ..database import Base


class Attribute(Base):
    __tablename__ = "attributes"
    id = Column(String, primary_key=True)
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
    event_uuid = Column(String)  # new
    attributeTag: list[str]  # new
