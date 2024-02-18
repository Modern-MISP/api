from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True)
    namespace = Column(String(255))
    description = Column(String(255))
    version = Column(String(255))
    enabled = Column(Boolean)
    exclusive = Column(Boolean)
    required = Column(Boolean)
    highlighted = Column(Boolean)


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id = Column(Integer, primary_key=True)
    taxonomy_id = Column(Integer, ForeignKey("taxonomies.id"))
    value = Column(String(255))
    expanded = Column(String(255))
    colour = Column(String(255))
    description = Column(String(255))
    exclusive = Column(Boolean)
    numerical_value = Column(Integer)


class TaxonomyEntry(Base):
    __tablename__ = "taxonomy_entries"

    id = Column(Integer, primary_key=True)
    taxonomy_predicate_id = Column(Integer, ForeignKey("taxonomy_predicates.id"))
    value = Column(String(255))
    expanded = Column(String(255))
    colour = Column(String(255))
    description = Column(String(255))
    numerical_value = Column(Integer)
