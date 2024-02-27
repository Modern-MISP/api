from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True, nullable=False)
    namespace = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)
    exclusive = Column(Boolean, default=False)
    required = Column(Boolean, nullable=False, default=False)
    highlighted = Column(Boolean)


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id = Column(Integer, primary_key=True, nullable=False)
    taxonomy_id = Column(Integer, ForeignKey("taxonomies.id"), nullable=False)
    value = Column(String(255), nullable=False)
    expanded = Column(String(255))
    colour = Column(String(255))
    description = Column(String(255))
    exclusive = Column(Boolean, default=False)
    numerical_value = Column(Integer)


class TaxonomyEntry(Base):
    __tablename__ = "taxonomy_entries"

    id = Column(Integer, primary_key=True, nullable=False)
    taxonomy_predicate_id = Column(Integer, ForeignKey("taxonomy_predicates.id"))
    value = Column(String(255), nullable=False)
    expanded = Column(String(255))
    colour = Column(String(255))
    description = Column(String(255))
    numerical_value = Column(Integer)
