from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from ..database import Base


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    meta_category = Column(String, index=True)
    description = Column(String)
    template_uuid = Column(String, index=True)
    template_version = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    uuid = Column(String, unique=True)
    timestamp = Column(Integer, index=True)
    distribution = Column(TINYINT, index=True)
    sharing_group_id = Column(Integer, index=True)
    comment = Column(String)
    deleted = Column(TINYINT)
    first_seen = Column(BigInteger, index=True)
    last_seen = Column(BigInteger, index=True)

    attributes = relationship("ObjectAttribute", backref="object")


class ObjectAttribute(Base):
    __tablename__ = "object_attributes"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, index=True)
    object_id = Column(Integer, ForeignKey("objects.id"), index=True)
    object_relation = Column(String)
    category = Column(String)
    type = Column(String)
    value1 = Column(String)
    value2 = Column(String)
    attribute_tag = Column(String)
    to_ids = Column(TINYINT)
    uuid = Column(String, unique=True)
    timestamp = Column(Integer)
    distribution = Column(TINYINT)
    sharing_group_id = Column(Integer, index=True)
    comment = Column(String)
    deleted = Column(TINYINT)
    disable_correlation = Column(TINYINT)
    first_seen = Column(BigInteger, index=True)
    last_seen = Column(BigInteger, index=True)
