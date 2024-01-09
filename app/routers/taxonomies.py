from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from ..schemas.taxonomy_schema import (
    Taxonomy,
    TaxonomyViewSchema,
    TaxonomyEntrySchema,
    TaxonomyAbleSchema,
    TaxonomyUpdateSchema
)


router = APIRouter(prefix="/taxonomies")


# Returns all taxonomies
@router.get("/")
async def get_taxonomies() -> List[TaxonomyViewSchema]:
    return TaxonomyViewSchema()


# Get Taxonomy by ID
@router.get("/view/{taxonomy_id_parameter}")  # deprecated
@router.get("/{taxonomy_id_parameter}")
async def get_taxonomy_by_id_depr() -> TaxonomyEntrySchema:
    return TaxonomyEntrySchema()


# Enable Taxonomy
@router.post("/enable/{taxonomiesId}")
async def enable_taxonomies() -> TaxonomyAbleSchema:
    return TaxonomyAbleSchema()


# Disable Taxonomies
@router.post("/disable/{taxonomiesId}")
async def disable_taxonomies() -> TaxonomyAbleSchema:
    return TaxonomyAbleSchema()


# Update Taxonomies.
@router.post("/taxonomies/update")  # Deprecated
@router.put("/taxonomies")
async def update_taxonomies_depr() -> TaxonomyUpdateSchema:
    return TaxonomyUpdateSchema()


# Get a Taxonomy extended with Tags used in events and attributes
@router.get("/taxonomy_tags/{taxonomyId}")
async def get_taxonomy_extended() -> TaxonomyEntrySchema:
    return TaxonomyEntrySchema()


@router.get("export/{taxonomyId}")
async def export_taxonomy():
    return {

    }
