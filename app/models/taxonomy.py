from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from ..database import Base


class Taxonomy(Base):
    id: Column(String)
    namespace: Column(String)
    description: Column(String)
    version: Column(String)
    exclusive: Column(Boolean)
    tag: Column(String)
    enabled: Column(Boolean)
    expanded: Column(String)
    required: Column(Boolean)
    highlighted: Column(Boolean)
    exclusive_predicate: Column(Boolean)
    existing_tag: Column(String) | relationship()
    entries: relationship("TaxonomyEntries", backref="Taxonomy")
    predicates: relationship("TaxonomyPredicate", backref="Taxonomy")
    values: relationship("TaxonomyValue", backref="Taxonomy")


class TaxonomyPredicate(Base):
    description: Column(String)
    value: Column(String)
    expanded: Column(String)


class TaxonomyValue(Base):
    predicate: Column(String)
    entries: relationship("TaxonomyEntry", backref="TaxonomyValue")


class TaxonomyEntry(Base):
    value: Column(String)
    expanded: Column(String)
    description: Column(String)


class TaxonomyEntries(Base):
    tag: Column(String)
    expanded: Column(String)
    exclusive_predicate: Column(Boolean)
    description: Column(String)
    existing_tag: Column(Boolean) |  relationship("TaxonomyTagSchema", backref="TaxonomyEntries")


class TaxonomyTagSchema(Base):
    id: Column(String)
    name: Column(String)
    colour: Column(String)
    exportable: Column(Boolean)
    org_id: Column(String)
    user_id: Column(String)
    hide_tag: Column(Boolean)
    numerical_value: Column(String)
    is_galaxy: Column(Boolean)
    is_custom_galaxy: Column(Boolean)
    inherited: Column(Integer)  # omitted
    attribute_count: Column(Integer)  # new
    count: Column(Integer)  # new
    favourite: Column(Integer)# new
    local_only: Column(Boolean)  # new
