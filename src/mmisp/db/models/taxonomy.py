from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True)
    namespace = Column(String)
    description = Column(String)
    version = Column(String)
    exclusive = Column(TINYINT)
    tag = Column(String)
    enabled = Column(TINYINT)
    expanded = Column(String)
    required = Column(TINYINT)
    highlighted = Column(Boolean)
    exclusive_predicate = Column(TINYINT)
    existing_tag = Column(String) | relationship()
    entries = relationship("TaxonomyEntries", backref="Taxonomy")
    predicates = relationship("TaxonomyPredicate", backref="Taxonomy")
    values = relationship("TaxonomyValue", backref="Taxonomy")


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id = Column(Integer, primary_key=True)
    taxonomy_id = Column(String, ForeignKey("taxonomies.id"))
    value = Column(String)
    expanded = Column(String)
    colour = Column(String)
    description = Column(String)
    exclusive = Column(TINYINT)
    numerical_value = Column(Integer)


class TaxonomyEntries(Base):
    __tablename__ = "taxonomy_entries"

    id = Column(Integer, primary_key=True)
    taxonomy_predicate_id = Column(Integer, ForeignKey("taxonomy_predicates.id"))
    value = Column(String)
    expanded = Column(String)
    colour = Column(String)
    description = Column(String)
    numerical_value = Column(Integer)
