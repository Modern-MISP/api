from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    meta_category = Column(String(255), index=True)
    description = Column(String(255))
    template_uuid = Column(String(255), index=True)
    template_version = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    uuid = Column(String(255), unique=True)
    timestamp = Column(Integer, index=True)
    distribution = Column(Integer, index=True)
    sharing_group_id = Column(Integer, index=True)
    comment = Column(String(255))
    deleted = Column(Integer)
    first_seen = Column(BigInteger, index=True)
    last_seen = Column(BigInteger, index=True)

    attributes = relationship("ObjectAttribute", backref="object")


class ObjectAttribute(Base):
    __tablename__ = "object_attributes"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, index=True)
    object_id = Column(Integer, ForeignKey(Object.id), index=True)
    object_relation = Column(String(255))
    category = Column(String(255))
    type = Column(String(255))
    value1 = Column(String(255))
    value2 = Column(String(255))
    attribute_tag = Column(String(255))
    to_ids = Column(Integer)
    uuid = Column(String(255), unique=True)
    timestamp = Column(Integer)
    distribution = Column(Integer)
    sharing_group_id = Column(Integer, index=True)
    comment = Column(String(255))
    deleted = Column(Integer)
    disable_correlation = Column(Integer)
    first_seen = Column(BigInteger, index=True)
    last_seen = Column(BigInteger, index=True)
