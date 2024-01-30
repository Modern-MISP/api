from fastapi import APIRouter

from mmisp.api_schemas.taxonomies.enable_disable_taxonomy_response import EnDisableTaxonomyResponse
from mmisp.api_schemas.taxonomies.export_taxonomies_response import ExportTaxonomyResponse
from mmisp.api_schemas.taxonomies.get_taxonomy_by_id_response import GetIdTaxonomyResponse
from mmisp.api_schemas.taxonomies.get_taxonomy_response import ViewTaxonomyResponse
from mmisp.api_schemas.taxonomies.update_taxonomy_response import UpdateTaxonomyResponse

router = APIRouter(tags=["taxonomies"])


# Get Taxonomy by ID
@router.get("/taxonomies/view/{taxonomy_id_parameter}")
@router.get("/taxonomies/{taxonomy_id_parameter}")
async def get_taxonomy_by_id() -> GetIdTaxonomyResponse:
    return GetIdTaxonomyResponse()


# Returns all taxonomies
@router.get("/taxonomies")
async def get_taxonomies() -> list[ViewTaxonomyResponse]:
    return ViewTaxonomyResponse()


# Get a Taxonomy extended with Tags used in events and attributes
@router.get("/taxonomies/taxonomy_tags/{taxonomyId}")
async def get_taxonomy_extended() -> GetIdTaxonomyResponse:
    return GetIdTaxonomyResponse()


# Export Taxonomy
@router.get("/taxonomies/export/{taxonomyId}")
async def export_taxonomy() -> ExportTaxonomyResponse:
    return ExportTaxonomyResponse()


# Enable Taxonomy
@router.post("/taxonomies/enable/{taxonomiesId}")
async def enable_taxonomies() -> EnDisableTaxonomyResponse:
    return EnDisableTaxonomyResponse()


# Disable Taxonomies
@router.post("/taxonomies/disable/{taxonomiesId}")
async def disable_taxonomies() -> EnDisableTaxonomyResponse:
    return EnDisableTaxonomyResponse()


# Update Taxonomies.
@router.post("/taxonomies/taxonomies/update")
async def update_taxonomies_depr() -> UpdateTaxonomyResponse:
    return UpdateTaxonomyResponse()


# --> Deprecated


# Get Taxonomy by ID
@router.get("/taxonomies/view/{taxonomy_id_parameter}", deprecated=True)  # deprecated
async def get_taxonomy_by_id_depr() -> GetIdTaxonomyResponse:
    return GetIdTaxonomyResponse()
