from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"
    id = Column(String, primary_key=True)
    name = Column(String)
    colour = Column(String)
    exportable = Column(Boolean)
    org_id = Column(String)
    user_id = Column(String)
    hide_tag = Column(Boolean)
    numerical_value = Column(String)
    is_galaxy = Column(Boolean)
    is_custom_galaxy = Column(Boolean)
    inherited = Column(Integer)


class Taxonomy(Base):
    __tablename__ = "tags_schema"
    id = Column(String, primary_key=True)
    namespace = Column(String)
    description = Column(String)
    version = Column(String)
    enabled = Column(Boolean)
    exclusive = Column(Boolean)
    required = Column(Boolean)


class TaxonomyPredicate(Base):
    __tablename__ = "predicate_feed"
    id = Column(String, primary_key=True)
    taxonomy_id = Column(String)
    value = Column(String)
    expanded = Column(String)
    colour = Column(String)
    description = Column(String)
    exclusive = Column(Boolean)
    numerical_value = Column(Integer)


class TagDelete(Base):
    __tablename__ = "delete_feed"
    name = Column(String, primary_key=True)
    message = Column(String)
    url = Column(String)


class TagSearch(Base):
    __tablename__ = "search_feeds"
    Tag: Tag
    Taxonomy: Taxonomy
    TaxonomyPredicate: TaxonomyPredicate
