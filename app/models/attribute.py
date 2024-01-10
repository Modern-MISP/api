from typing import List

from sqlalchemy import Boolean, Column, String

from ..database import Base


class Attribute(Base):
    __tablename__ = "attribute"
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

    class Config:
        orm_mode = True


class AttributeRestSearch(Base):
    __tablename__ = "attributeRestSearch"
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

    class Config:
        orm_mode = True


class AttributeAdd(Base):
    __tablename__ = "attributeAdd"
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
    attributeTag: List[str]  # new

    class Config:
        orm_mode = True


class AttributeEdit(Base):
    __tablename__ = "attributeEdit"
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
    event_uuid = Column(String)  # new

    class Config:
        orm_mode = True


class AttributeDelete(Base):
    __tablename__ = "attributeDelete"
    message = Column(String)

    class Config:
        orm_mode = True


class AttributeDeleteSelected(Base):
    __tablename__ = "attributeDeleteSelected"
    saved = Column(Boolean)
    success = Column(Boolean)
    name = Column(String)
    message = Column(String)
    url = Column(String)
    id = Column(String)

    class Config:
        orm_mode = True


class AttributeGetById(Base):
    __tablename__ = "attributeGetById"
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
    event_uuid = Column(String)  # new
    attributeTag: List[str]  # new

    class Config:
        orm_mode = True


class AttributeFreeTextImport(Base):
    __tablename__ = "attributeFreeTextImport"
    comment = Column(String)
    value = Column(String)
    original_value = Column(String)
    to_ids = Column(String)
    type = Column(String)
    category = Column(String)
    distribution = Column(String)

    class Config:
        orm_mode = True


class AttributeTag(Base):
    __tablename__ = "attributeTag"
    saved = Column(Boolean)
    success = Column(String)
    check_publish = Column(Boolean)

    class Config:
        orm_mode = True


class ShadowAttribute(Base):
    __tablename__ = "shadowAttribute"
    value = Column(String)
    to_ids = Column(Boolean)
    type = Column(String)
    category = Column(String)
