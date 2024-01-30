from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True)
    namespace = Column(String(255))
    description = Column(String(255))
    version = Column(String(255))
    exclusive = Column(Boolean)
    tag = Column(String(255))
    enabled = Column(Boolean)
    expanded = Column(String(255))  # TODO value does not show up in misp01, misp02 database
    # + is not specified in MYSQL.sql, do we need this since value is already set on TaxonomyPredicate?
    required = Column(Boolean)
    highlighted = Column(Boolean)
    exclusive_predicate = Column(Boolean)  # TODO same here, do we need this?
    existing_tag = Column(String(255))
    # entries = relationship("TaxonomyEntries", backref="Taxonomy")
    # predicates = relationship("TaxonomyPredicate", backref="Taxonomy")
    # values = relationship("TaxonomyValue", backref="Taxonomy")


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id = Column(Integer, primary_key=True)
    taxonomy_id = Column(Integer, ForeignKey(Taxonomy.id))
    value = Column(String(255))
    expanded = Column(String(255))
    colour = Column(String(255))
    description = Column(String(255))
    exclusive = Column(Boolean)
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
