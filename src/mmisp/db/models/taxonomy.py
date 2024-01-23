from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True)
    namespace = Column(String(255))
    description = Column(String(255))
    version = Column(String(255))
    exclusive = Column(TINYINT)
    tag = Column(String(255))
    enabled = Column(TINYINT)
    expanded = Column(String(255))
    required = Column(TINYINT)
    highlighted = Column(Boolean)
    exclusive_predicate = Column(TINYINT)
    existing_tag = Column(String(255))
    entries = relationship("TaxonomyEntries", backref="Taxonomy")
    predicates = relationship("TaxonomyPredicate", backref="Taxonomy")
    values = relationship("TaxonomyValue", backref="Taxonomy")


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id = Column(Integer, primary_key=True)
    taxonomy_id = Column(Integer, ForeignKey(Taxonomy.id))
    value = Column(String(255))
    expanded = Column(String(255))
    colour = Column(String(255))
    description = Column(String(255))
    exclusive = Column(TINYINT)
    numerical_value = Column(Integer)


class TaxonomyEntries(Base):
    __tablename__ = "taxonomy_entries"

    id = Column(Integer, primary_key=True)
    taxonomy_predicate_id = Column(Integer, ForeignKey(TaxonomyPredicate.id))
    value = Column(String(255))
    expanded = Column(String(255))
    colour = Column(String(255))
    description = Column(String(255))
    numerical_value = Column(Integer)
