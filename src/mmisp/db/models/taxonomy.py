from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True, nullable=False)
    namespace = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)
    exclusive = Column(Boolean, default=False)
    required = Column(Boolean, nullable=False, default=False)
    highlighted = Column(Boolean)


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id = Column(Integer, primary_key=True, nullable=False)
    taxonomy_id = Column(Integer, ForeignKey(Taxonomy.id), nullable=False, index=True)
    value = Column(Text, nullable=False)
    expanded = Column(Text)
    colour = Column(String(7))
    description = Column(Text)
    exclusive = Column(Boolean, default=False)
    numerical_value = Column(Integer, index=True)


class TaxonomyEntry(Base):
    __tablename__ = "taxonomy_entries"

    id = Column(Integer, primary_key=True, nullable=False)
    taxonomy_predicate_id = Column(Integer, ForeignKey(TaxonomyPredicate.id), nullable=False, index=True)
    value = Column(Text, nullable=False)
    expanded = Column(Text)
    colour = Column(String(7))
    description = Column(Text)
    numerical_value = Column(Integer, index=True)
