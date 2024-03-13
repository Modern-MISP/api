from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.standard_status_response import StandardStatusIdentifiedResponse, StandardStatusResponse
from mmisp.api_schemas.taxonomies.export_taxonomies_response import (
    ExportTaxonomyEntry,
    ExportTaxonomyResponse,
    TaxonomyPredicateSchema,
    TaxonomyValueSchema,
)
from mmisp.api_schemas.taxonomies.get_taxonomy_by_id_response import (
    GetIdTaxonomyResponse,
    GetIdTaxonomyResponseWrapper,
    TaxonomyEntrySchema,
)
from mmisp.api_schemas.taxonomies.get_taxonomy_response import (
    TaxonomyView,
    ViewTaxonomyResponse,
    ViewTaxonomyResponseWrapper,
)
from mmisp.api_schemas.taxonomies.get_taxonomy_tags_response import (
    GetTagTaxonomyResponse,
    TaxonomyTagEntrySchema,
)
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.attribute import AttributeTag
from mmisp.db.models.event import EventTag
from mmisp.db.models.tag import Tag
from mmisp.db.models.taxonomy import Taxonomy, TaxonomyEntry, TaxonomyPredicate
from mmisp.util.partial import partial

router = APIRouter(tags=["taxonomies"])


@router.put(
    "/taxonomies",
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Update taxonomies",
    description="Update all taxonomies.",
)
@with_session_management
async def update_taxonomies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _update_taxonomies(db, False)


@router.get(
    "/taxonomies/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetIdTaxonomyResponse),
    summary="Get taxonomy details",
    description="Retrieve details of a specific taxonomy by its ID.",
)
@with_session_management
async def get_taxonomy_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> dict:
    return await _get_taxonomy_details(db, taxonomy_id)


@router.get(
    "/taxonomies",
    status_code=status.HTTP_200_OK,
    response_model=partial(ViewTaxonomyResponseWrapper),
    summary="Get all taxonomies",
    description="Retrieve a list of all taxonomies.",
)
@with_session_management
async def get_taxonomies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _get_all_taxonomies(db)


@router.get(
    "/taxonomies/taxonomy_tags/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetTagTaxonomyResponse),
    summary="Get taxonomy inclusive tags and attributes",
    description="Retrieve details of a specific taxonomy and its tags and attributes by its ID.",
)
@with_session_management
async def get_taxonomy_details_extended(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> dict:
    return await _get_taxonomy_details_extended(db, taxonomy_id)


@router.get(
    "/taxonomies/export/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(ExportTaxonomyResponse),
    summary="Export taxonomy",
    description="Export taxonomy.",
)
@with_session_management
async def export_taxonomy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> dict:
    return await _export_taxonomy(db, taxonomy_id)


@router.post(
    "/taxonomies/enable/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Enable taxonomy",
    description="Enable a specific taxonomy by its ID.",
)
@with_session_management
async def enable_taxonomy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> dict:
    return await _enable_taxonomy(db, taxonomy_id)


@router.post(
    "/taxonomies/disable/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Disable taxonomy",
    description="Disable a specific taxonomy by its ID.",
)
@with_session_management
async def disable_taxonomies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> dict:
    return await _disable_taxonomy(db, taxonomy_id)


@router.post(
    "/taxonomies/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Update taxonomies",
    description="Update all taxonomies.",
)
@with_session_management
async def update_taxonomies_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _update_taxonomies(db, True)


@router.get(
    "/taxonomies/view/{taxonomyId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(GetIdTaxonomyResponse),
    summary="Get taxonomy details",
    description="Retrieve details of a specific taxonomy by its ID.",
)
@with_session_management
async def get_taxonomy_by_id_depr(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    taxonomy_id: Annotated[int, Path(..., alias="taxonomyId")],
) -> GetIdTaxonomyResponseWrapper:
    return await _get_taxonomy_details(db, taxonomy_id)


# --- endpoint logic ---


async def _update_taxonomies(db: Session, deprecated: bool) -> dict:
    db.query(Taxonomy).all()
    number_updated_taxonomies = db.query(Taxonomy).count()
    saved = True
    success = True
    name = "Succesfully updated " + str(number_updated_taxonomies) + "taxonomies."
    message = "Succesfully updated " + str(number_updated_taxonomies) + "taxonomies."
    url = "/taxonomies/update" if deprecated else "/taxonomies"

    return StandardStatusResponse(
        saved=saved,
        success=success,
        name=name,
        message=message,
        url=url,
    )


async def _get_taxonomy_details(db: Session, taxonomy_id: int) -> dict:
    taxonomy: Taxonomy | None = db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    taxonomy_predicates = db.query(TaxonomyPredicate).filter(TaxonomyPredicate.taxonomy_id == taxonomy.id).all()
    taxonomy_entries: list[TaxonomyEntry] = []
    for taxonomy_predicate in taxonomy_predicates:
        taxonomy_entries_of_taxonomy_predicate = (
            db.query(TaxonomyEntry).filter(TaxonomyEntry.taxonomy_predicate_id == taxonomy_predicate.id).all()
        )
        for taxonomy_entry_of_taxonomy_predicate in taxonomy_entries_of_taxonomy_predicate:
            tag_name = _get_tag_name(db, taxonomy_entry_of_taxonomy_predicate)

            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag:
                existing_tag = tag.__dict__
            else:
                existing_tag = False

            taxonomy_entries.append(
                TaxonomyEntrySchema(
                    tag=tag_name,
                    expanded=taxonomy_predicate.expanded + ":" + taxonomy_entry_of_taxonomy_predicate.expanded,
                    exclusive_predicate=taxonomy_predicate.exclusive,
                    description=taxonomy_entry_of_taxonomy_predicate.description,
                    existing_tag=existing_tag,
                )
            )

    return {**taxonomy.__dict__, "entries": taxonomy_entries}


async def _get_all_taxonomies(db: Session) -> dict:
    taxonomies = db.query(Taxonomy).all()
    response = []

    for taxonomy in taxonomies:
        query = (
            db.query(TaxonomyEntry)
            .join(TaxonomyPredicate, TaxonomyPredicate.id == TaxonomyEntry.taxonomy_predicate_id)
            .filter(TaxonomyPredicate.taxonomy_id == taxonomy.id)
        )
        total_count = query.count()
        taxonomy_predicates = db.query(TaxonomyPredicate).all()
        for taxonomy_predicate in taxonomy_predicates:
            if (
                db.query(TaxonomyEntry).filter(TaxonomyEntry.taxonomy_predicate_id == taxonomy_predicate.id).first()
                is None
            ):
                total_count += 1

        current_count = 0
        for taxonomy_entry in query.all():
            tag_name = _get_tag_name(db, taxonomy_entry)
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag:
                current_count += 1

        taxonomy_response = ViewTaxonomyResponse(
            Taxonomy=TaxonomyView(
                id=taxonomy.id,
                namespace=taxonomy.namespace,
                description=taxonomy.description,
                version=taxonomy.version,
                enabled=taxonomy.enabled,
                exclusive=taxonomy.exclusive,
                required=taxonomy.required,
                highlighted=taxonomy.highlighted,
            ),
            total_count=total_count,
            current_count=current_count,
        )
        response.append(taxonomy_response)

    return ViewTaxonomyResponseWrapper(taxonomies=response)


async def _get_taxonomy_details_extended(db: Session, taxonomy_id: int) -> dict:
    taxonomy: Taxonomy | None = db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    taxonomy_predicates = db.query(TaxonomyPredicate).filter(TaxonomyPredicate.taxonomy_id == taxonomy.id).all()
    taxonomy_entries: list[TaxonomyTagEntrySchema] = []
    for taxonomy_predicate in taxonomy_predicates:
        taxonomy_entries_of_taxonomy_predicate = (
            db.query(TaxonomyEntry).filter(TaxonomyEntry.taxonomy_predicate_id == taxonomy_predicate).all()
        )
        for taxonomy_entry_of_taxonomy_predicate in taxonomy_entries_of_taxonomy_predicate:
            tag_name = _get_tag_name(db, taxonomy_entry_of_taxonomy_predicate)
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag:
                events = db.query(EventTag).filter(EventTag.tag_id == tag.id).count()
                attributes = db.query(AttributeTag).filter(AttributeTag.tag_id == tag.id).count()
                existing_tag = tag.__dict__
            else:
                existing_tag = False

            taxonomy_entries.append(
                TaxonomyTagEntrySchema(
                    tag=tag_name,
                    expanded=taxonomy_predicate.expand + ":" + taxonomy_entry_of_taxonomy_predicate.expanded,
                    exclusive_predicate=taxonomy_predicate.exclusive,
                    description=taxonomy_entries_of_taxonomy_predicate.description,
                    existing_tag=existing_tag,
                    events=events,
                    attributes=attributes,
                )
            )

    response = {**taxonomy.__dict__, "entries": taxonomy_entries}
    return response.__dict__


async def _export_taxonomy(db: Session, taxonomy_id: int) -> dict:
    taxonomy: Taxonomy | None = db.get(Taxonomy, taxonomy_id)

    if not Taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    predicates: list[TaxonomyPredicateSchema] = []
    values: list[TaxonomyValueSchema] = []

    taxonomy_predicates = db.query(TaxonomyPredicate).filter(TaxonomyPredicate.taxonomy_id == taxonomy_id)
    for taxonomy_predicate in taxonomy_predicates:
        predicates.append(TaxonomyPredicateSchema(**taxonomy_predicate.__dict__))
        taxonomy_entries = (
            db.query(TaxonomyEntry).filter(TaxonomyEntry.taxonomy_predicate_id == taxonomy_predicate.id).all()
        )
        for taxonomy_entry in taxonomy_entries:
            values.append(ExportTaxonomyEntry(**taxonomy_entry.__dict__))

    return {**taxonomy.__dict__, "predicates": predicates, "values": values}


async def _enable_taxonomy(db: Session, taxonomy_id: int) -> dict:
    taxonomy: Taxonomy | None = db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    taxonomy.enabled = True

    db.commit()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="Taxonomy enabled",
        message="Taxonomy enabled",
        url=f"/taxonomies/enable/{taxonomy_id}",
        id=taxonomy_id,
    )


async def _disable_taxonomy(db: Session, taxonomy_id: int) -> dict:
    taxonomy: Taxonomy | None = db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    taxonomy.enabled = False

    db.commit()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="Taxonomy disabled",
        message="Taxonomy disabled",
        url=f"/taxonomies/disable/{taxonomy_id}",
        id=taxonomy_id,
    )


def _get_tag_name(db: Session, taxonomy_entry: TaxonomyEntry) -> str:
    taxonomy_predicate = (
        db.query(TaxonomyPredicate).filter(TaxonomyPredicate.id == taxonomy_entry.taxonomy_predicate_id).first()
    )
    taxonomy = db.query(Taxonomy).filter(Taxonomy.id == taxonomy_predicate.taxonomy_id).first()
    return taxonomy.namespace + ":" + taxonomy_predicate.value + '="' + taxonomy_entry.value + '"'
