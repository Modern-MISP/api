from fastapi import APIRouter

from mmisp.api_schemas.taxonomies.enable_disable_taxonomy_out import TaxonomyAbleSchema
from mmisp.api_schemas.taxonomies.export_taxonomies_out import TaxonomyExportSchema
from mmisp.api_schemas.taxonomies.get_taxonomy_by_id_out import TaxonomyTagSchema
from mmisp.api_schemas.taxonomies.get_taxonomy_out import TaxonomyViewSchema
from mmisp.api_schemas.taxonomies.update_taxonomy_out import TaxonomyUpdateSchema

router = APIRouter(prefix="/taxonomies")


# Returns all taxonomies
@router.get("/")
async def get_taxonomies() -> list[TaxonomyViewSchema]:
    return TaxonomyViewSchema()


# Get Taxonomy by ID
@router.get("/view/{taxonomy_id_parameter}", deprecated=True)  # deprecated
@router.get("/{taxonomy_id_parameter}")
async def get_taxonomy_by_id_depr() -> TaxonomyTagSchema:
    return TaxonomyTagSchema()


# Enable Taxonomy
@router.post("/enable/{taxonomiesId}")
async def enable_taxonomies() -> TaxonomyAbleSchema:
    return TaxonomyAbleSchema()


# Disable Taxonomies
@router.post("/disable/{taxonomiesId}")
async def disable_taxonomies() -> TaxonomyAbleSchema:
    return TaxonomyAbleSchema()


# Update Taxonomies.
@router.post(
    "/taxonomies/update", deprecated=True
)  # Deprecated Sollte wahrscheinlich nicht deprecated sein
@router.put("/taxonomies")
async def update_taxonomies_depr() -> TaxonomyUpdateSchema:
    return TaxonomyUpdateSchema()


# Get a Taxonomy extended with Tags used in events and attributes
@router.get("/taxonomy_tags/{taxonomyId}")
async def get_taxonomy_extended() -> TaxonomyTagSchema:
    return TaxonomyTagSchema()


@router.get("export/{taxonomyId}")
async def export_taxonomy():
    return TaxonomyExportSchema()
