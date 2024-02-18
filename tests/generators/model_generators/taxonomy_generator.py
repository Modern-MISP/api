from time import time

from mmisp.db.models.taxonomy import Taxonomy, TaxonomyEntry, TaxonomyPredicate


def generate_taxonomy() -> Taxonomy:
    return Taxonomy(
        namespace=f"test taxonomy {time()}",
        description="this is a description",
        version=1,
        enabled=True,
        exclusive=True,
        required=True,
        highlighted=True,
    )


def generate_taxonomy_predicate(taxonomy_id: int) -> TaxonomyPredicate:
    """These fields need to be set manually: taxonomy_id"""
    return TaxonomyPredicate(
        taxonomy_id=taxonomy_id,
        value="this is value",
        expanded="this expand",
        colour="#123456",
        description="this is a description",
        exclusive=True,
        numerical_value=1,
    )


def generate_taxonomy_entry(taxonomy_predicate_id: int) -> TaxonomyEntry:
    """These fields need to be set manually: taxonomy_predicate_id"""
    return TaxonomyEntry(
        taxonomy_predicate_id=taxonomy_predicate_id,
        value="this is a value",
        expanded="this expand",
        colour="#123456",
        description="this is a description",
        numerical_value=1,
    )
