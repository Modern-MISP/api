from fastapi import APIRouter

from mmisp.api_schemas.taxonomies.enable_disable_taxonomy_out import TaxonomyAbleSchema
from mmisp.api_schemas.taxonomies.export_taxonomies_out import TaxonomyExportSchema
from mmisp.api_schemas.taxonomies.get_taxonomy_by_id_out import TaxonomyTagSchema
from mmisp.api_schemas.taxonomies.get_taxonomy_out import TaxonomyViewSchema
from mmisp.api_schemas.taxonomies.update_taxonomy_out import TaxonomyUpdateSchema

router = APIRouter(tags=["taxonomies"])


# Get Taxonomy by ID
@router.get("/taxonomies/view/{taxonomy_id_parameter}", deprecated=True)  # deprecated
@router.get("/taxonomies/{taxonomy_id_parameter}")
async def get_taxonomy_by_id_depr() -> TaxonomyTagSchema:
    return TaxonomyTagSchema()


# Returns all taxonomies
@router.get("/taxonomies")
async def get_taxonomies() -> list[TaxonomyViewSchema]:
    return TaxonomyViewSchema()


# Get a Taxonomy extended with Tags used in events and attributes
@router.get("/taxonomies/taxonomy_tags/{taxonomyId}")
async def get_taxonomy_extended() -> TaxonomyTagSchema:
    return TaxonomyTagSchema()


# Export Taxonomy
@router.get("/taxonomies/export/{taxonomyId}")
async def export_taxonomy():
    return TaxonomyExportSchema()


# Enable Taxonomy
@router.post("/taxonomies/enable/{taxonomiesId}")
async def enable_taxonomies() -> TaxonomyAbleSchema:
    return TaxonomyAbleSchema()


# Disable Taxonomies
@router.post("/taxonomies/disable/{taxonomiesId}")
async def disable_taxonomies() -> TaxonomyAbleSchema:
    return TaxonomyAbleSchema()


# Update Taxonomies.
@router.post("/taxonomies/taxonomies/update")
async def update_taxonomies_depr() -> TaxonomyUpdateSchema:
    return TaxonomyUpdateSchema()


# --> Deprecated


# Get Taxonomy by ID
@router.get("/taxonomies/view/{taxonomy_id_parameter}", deprecated=True)  # deprecated
async def get_taxonomy_by_id_depr() -> TaxonomyTagSchema:
    return TaxonomyTagSchema()
