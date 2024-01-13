from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    colour = Column(String)
    exportable = Column(Boolean)
    org_id = Column(String)
    user_id = Column(String)
    hide_tag = Column(Boolean)
    numerical_value = Column(String)
    is_galaxy = Column(Boolean)
    is_custom_galaxy = Column(Boolean)
    attribute_count = Column(Integer)  # new
    count = Column(Integer)  # new
    favourite = Column(Boolean)  # new
    local_only = Column(Boolean)  # new


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True)
    namespace = Column(String)
    description = Column(String)
    version = Column(String)
    enabled = Column(Boolean)
    exclusive = Column(Boolean)
    required = Column(Boolean)

    predicates = relationship("TaxonomyPredicate", backref="taxonomy")


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id = Column(Integer, primary_key=True)
    taxonomy_id = Column(String, ForeignKey("taxonomies.id"))
    value = Column(String)
    expanded = Column(String)
    colour = Column(String)
    description = Column(String)
    exclusive = Column(Boolean)
    numerical_value = Column(Integer)
