from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(String)
    namespace = Column(String)
    description = Column(String)
    version = Column(String)
    exclusive = Column(Boolean)
    tag = Column(String)
    enabled = Column(Boolean)
    expanded = Column(String)
    required = Column(Boolean)
    highlighted = Column(Boolean)
    exclusive_predicate = Column(Boolean)
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

    tag = Column(String)
    expanded = Column(String)
    exclusive_predicate = Column(Boolean)
    description = Column(String)
    existing_tag = Column(Boolean) | relationship(
        "TaxonomyTagSchema", backref="TaxonomyEntries"
    )
