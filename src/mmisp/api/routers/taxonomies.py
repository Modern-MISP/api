import typing
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.responses.standard_status_response import (
    StandardStatusIdentifiedResponse,
    StandardStatusResponse,
)
from mmisp.api_schemas.tags import TagAttributesResponse
from mmisp.api_schemas.taxonomies import (
    ExportTaxonomyEntry,
    ExportTaxonomyResponse,
    GetIdTaxonomyResponse,
    GetIdTaxonomyResponseWrapper,
    GetTagTaxonomyResponse,
    TaxonomyEntrySchema,
    TaxonomyPredicateSchema,
    TaxonomyTagEntrySchema,
    TaxonomyValueSchema,
    TaxonomyView,
    ViewTaxonomyResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import AttributeTag
from mmisp.db.models.event import EventTag
from mmisp.db.models.tag import Tag
from mmisp.db.models.taxonomy import Taxonomy, TaxonomyEntry, TaxonomyPredicate
from mmisp.lib.logger import alog

router = APIRouter(tags=["taxonomies"])


@router.put(
    "/taxonomies",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update taxonomies",
)
@alog
async def update_taxonomies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    """
    Update all taxonomies.

    args:

    - auth: Authentication details

    - db: Database session

    returns:

    - StandardStatusResponse: Status response indicating success or failure
    """
    return await _update_taxonomies(db, False)


@router.get(
    "/taxonomies",
    status_code=status.HTTP_200_OK,
    summary="Get all taxonomies",
)
@router.get(
    "/taxonomies/index",
    status_code=status.HTTP_200_OK,
    summary="Get all taxonomies",
)
@alog
async def get_taxonomies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[ViewTaxonomyResponse]:
    """
    Retrieve a list of all taxonomies.

    args:

    - auth: Authentication details

    - db: Database session

    returns:

    - list[ViewTaxonomyResponse]: List of taxonomies
    """
    return await _get_all_taxonomies(db)


@router.get(
    "/taxonomies/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=GetIdTaxonomyResponseWrapper,
    summary="Get taxonomy details",
)
@alog
async def get_taxonomy_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> GetIdTaxonomyResponseWrapper:
    """
    Retrieve details of a specific taxonomy by its ID.

    args:

    - auth: Authentication details

    - db: Database session

    - taxonomy_id: ID of the taxonomy to retrieve

    returns:

    - GetIdTaxonomyResponseWrapper: Wrapper containing taxonomy details
    """
    return await _get_taxonomy_details(db, taxonomy_id)


@router.get(
    "/taxonomies/taxonomy_tags/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=GetTagTaxonomyResponse,
    summary="Get taxonomy inclusive tags and attributes",
)
@alog
async def get_taxonomy_details_extended(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> GetTagTaxonomyResponse:
    """
    Retrieve details of a specific taxonomy and its tags and attributes by its ID.

    args:

    - auth: Authentication details

    - db: Database session

    - taxonomy_id: ID of the taxonomy to retrieve extended details for

    returns:

    - GetTagTaxonomyResponse: Response containing taxonomy attributes
    """
    return await _get_taxonomy_details_extended(db, taxonomy_id)


@router.get(
    "/taxonomies/export/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=ExportTaxonomyResponse,
    summary="Export taxonomy",
)
@alog
async def export_taxonomy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> ExportTaxonomyResponse:
    """
    Export taxonomy.

    args:

    - auth: Authentication details

    - db: Database session

    - taxonomy_id: ID of the taxonomy to export

    returns:

    - ExportTaxonomyResponse: Response containing exported taxonomy data
    """
    return await _export_taxonomy(db, taxonomy_id)


@router.post(
    "/taxonomies/enable/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Enable taxonomy",
)
@alog
async def enable_taxonomy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> StandardStatusResponse:
    """
    Enable a specific taxonomy by its ID.

    args:

    - auth: Authentication details

    - db: Database session

    - taxonomy_id: ID of the taxonomy to enable

    returns:

    - StandardStatusResponse: Status response indicating success or failure
    """
    return await _enable_taxonomy(db, taxonomy_id)


@router.post(
    "/taxonomies/disable/{taxonomyId}",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Disable taxonomy",
)
@alog
async def disable_taxonomies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    taxonomy_id: Annotated[int, Path(alias="taxonomyId")],
) -> StandardStatusResponse:
    """
    Disable a specific taxonomy by its ID.

    args:

    - auth: Authentication details

    - db: Database session

    - taxonomy_id: ID of the taxonomy to disable

    returns:

    - StandardStatusResponse: Status response indicating success or failure
    """
    return await _disable_taxonomy(db, taxonomy_id)


@router.post(
    "/taxonomies/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update taxonomies",
)
@alog
async def update_taxonomies_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    """
    Update all taxonomies.

    args:

    - auth: Authentication details

    - db: Database session

    returns:

    - StandardStatusResponse: Status response indicating success or failure
    """
    return await _update_taxonomies(db, True)


@router.get(
    "/taxonomies/view/{taxonomyId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=GetIdTaxonomyResponseWrapper,
    summary="Get taxonomy details",
)
@alog
async def get_taxonomy_by_id_depr(
    db: Annotated[Session, Depends(get_db)],
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    taxonomy_id: Annotated[int, Path(..., alias="taxonomyId")],
) -> GetIdTaxonomyResponseWrapper:
    """
    Retrieve details of a specific taxonomy by its ID.

    args:

    - db: Database session

    - auth: Authentication details

    - taxonomy_id: ID of the taxonomy to get

    returns:

    - GetIdTaxonomyResponseWrapper: Wrapper containing taxonomy details
    """
    return await _get_taxonomy_details(db, taxonomy_id)


# --- endpoint logic ---


@alog
async def _update_taxonomies(db: Session, deprecated: bool) -> StandardStatusResponse:
    result = await db.execute(select(func.count()).select_from(Taxonomy))
    number_updated_taxonomies = result.scalar()
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


@alog
async def _get_taxonomy_details(db: Session, taxonomy_id: int) -> GetIdTaxonomyResponseWrapper:
    taxonomy: Taxonomy | None = await db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    result = await db.execute(select(TaxonomyPredicate).filter(TaxonomyPredicate.taxonomy_id == taxonomy.id))
    taxonomy_predicates = result.scalars().all()

    taxonomy_entries: list[TaxonomyEntrySchema] = []
    for taxonomy_predicate in taxonomy_predicates:
        result = await db.execute(
            select(TaxonomyEntry).filter(TaxonomyEntry.taxonomy_predicate_id == taxonomy_predicate.id)
        )
        taxonomy_entries_of_taxonomy_predicate = result.scalars().all()

        for taxonomy_entry_of_taxonomy_predicate in taxonomy_entries_of_taxonomy_predicate:
            tp_expanded = taxonomy_predicate.expanded
            tpe_expanded = taxonomy_entry_of_taxonomy_predicate.expanded
            if tp_expanded is None:
                tp_expanded = taxonomy_predicate.value
            if tpe_expanded is None:
                tpe_expanded = taxonomy_entry_of_taxonomy_predicate.value
            expanded = tp_expanded + ":" + tpe_expanded

            tag_name = await _get_tag_name(db, taxonomy_entry_of_taxonomy_predicate)

            result = await db.execute(select(Tag).filter(Tag.name == tag_name).limit(1))
            tag = result.scalars().first()
            if tag:
                existing_tag: TagAttributesResponse | bool = TagAttributesResponse.parse_obj(tag.__dict__)
            else:
                existing_tag = False

            taxonomy_entries.append(
                TaxonomyEntrySchema(
                    tag=tag_name,
                    expanded=expanded,
                    exclusive_predicate=taxonomy_predicate.exclusive,
                    description=taxonomy_entry_of_taxonomy_predicate.description,
                    existing_tag=existing_tag,
                )
            )

    response = GetIdTaxonomyResponseWrapper(
        Taxonomy=GetIdTaxonomyResponse(
            id=taxonomy.id,
            namespace=taxonomy.namespace,
            description=taxonomy.description,
            version=taxonomy.version,
            enabled=taxonomy.enabled,
            exclusive=taxonomy.exclusive,
            required=taxonomy.required,
            highlighted=taxonomy.highlighted,
            entries=taxonomy_entries,
        )
    )
    return response


@alog
async def _get_all_taxonomies(db: Session) -> list[ViewTaxonomyResponse]:
    query = select(Taxonomy).options(selectinload(Taxonomy.predicates).selectinload(TaxonomyPredicate.entries))
    result = await db.execute(query)
    taxonomies: Sequence[Taxonomy] = result.scalars().all()

    response: list[ViewTaxonomyResponse] = []
    #    tag_names = []
    #    taxonomy_entries_predicates = []
    #    taxonomy_entries_builder = []

    #    result2 = await db.execute(select(Tag.name))
    #    tag_names_retrieve: Sequence[str] = result2.scalars().all()
    #
    #    result3 = await db.execute(
    #        select(TaxonomyPredicate.taxonomy_id, TaxonomyPredicate.value, TaxonomyEntry.value)
    #        .outerjoin(TaxonomyEntry, TaxonomyPredicate.id == TaxonomyEntry.taxonomy_predicate_id)
    #        .order_by(TaxonomyPredicate.taxonomy_id)
    #    )
    #    taxonomy_entries_predicates_db = result3.all()
    #
    #    result4 = await db.execute(
    #        select(TaxonomyPredicate.taxonomy_id, func.count(TaxonomyPredicate.taxonomy_id))
    #        .outerjoin(TaxonomyEntry, TaxonomyPredicate.id == TaxonomyEntry.taxonomy_predicate_id)
    #        .group_by(TaxonomyPredicate.taxonomy_id)
    #    )
    #    total_count_db = result4.all()
    #
    #    for tag in tag_names_retrieve:
    #        if ":" in tag:
    #            tag_names.append(tag)
    #
    #    current_taxonomy_id = 1
    #
    #    for taxonomy_entry in taxonomy_entries_predicates_db:
    #        if taxonomy_entry[0] == current_taxonomy_id:
    #            taxonomy_entries_builder.append(taxonomy_entry)
    #            continue
    #
    #        current_taxonomy_id = taxonomy_entry[0]
    #        taxonomy_entries_predicates.append(taxonomy_entries_builder[:])
    #        taxonomy_entries_builder.clear()
    #        taxonomy_entries_builder.append(taxonomy_entry)
    #
    #    taxonomy_entries_predicates.append(taxonomy_entries_builder)

    for taxonomy in taxonomies:
        #        total_count = total_count_db[taxonomy.id - 1][1]
        for predicate in taxonomy.predicates:
            for taxonomy_entry in predicate.entries:
                tag_name = str(taxonomy.namespace) + ":" + predicate.value
                tag_name_entry = f'{tag_name}="{taxonomy_entry.value}"'
                assert tag_name_entry

        total_count = len(taxonomy.predicates)
        current_count = 0  # TODO: recalculate tag exist count
        #        for taxonomy_entry in taxonomy_entries_predicates[taxonomy.id - 1]:
        #            tag_name = str(taxonomy.namespace) + ":" + taxonomy_entry[1]
        #            entry_val = taxonomy_entry[2] if taxonomy_entry[2] is not None else ""
        #            if tag_name in tag_names or tag_name + '="' + entry_val + '"' in tag_names:
        #                current_count += 1

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

    return response


@alog
async def _get_taxonomy_details_extended(db: Session, taxonomy_id: int) -> GetTagTaxonomyResponse:
    taxonomy: Taxonomy | None = await db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    result = await db.execute(select(TaxonomyPredicate).filter(TaxonomyPredicate.taxonomy_id == taxonomy.id))
    taxonomy_predicates = result.scalars().all()

    taxonomy_entries: list[TaxonomyTagEntrySchema] = []

    for taxonomy_predicate in taxonomy_predicates:
        result = await db.execute(
            select(TaxonomyEntry).filter(TaxonomyEntry.taxonomy_predicate_id == taxonomy_predicate.id)
        )
        taxonomy_entries_of_taxonomy_predicate = result.scalars().all()

        for taxonomy_entry_of_taxonomy_predicate in taxonomy_entries_of_taxonomy_predicate:
            tp_expanded = taxonomy_predicate.expanded
            tpe_expanded = taxonomy_entry_of_taxonomy_predicate.expanded
            if tp_expanded is None:
                tp_expanded = taxonomy_predicate.value
            if tpe_expanded is None:
                tpe_expanded = taxonomy_entry_of_taxonomy_predicate.value
            expanded = tp_expanded + ":" + tpe_expanded
            events = 0
            attributes = 0
            tag_name = await _get_tag_name(db, taxonomy_entry_of_taxonomy_predicate)

            result = await db.execute(select(Tag).filter(Tag.name == tag_name).limit(1))
            tag = result.scalars().first()

            if tag:
                result = await db.execute(select(func.count()).select_from(EventTag).filter(EventTag.tag_id == tag.id))
                events = typing.cast(int, result.scalar())

                result = await db.execute(
                    select(func.count()).select_from(AttributeTag).filter(AttributeTag.tag_id == tag.id)
                )
                attributes = typing.cast(int, result.scalar())

                existing_tag: dict | bool = tag.__dict__
            else:
                existing_tag = False

            taxonomy_entries.append(
                TaxonomyTagEntrySchema(
                    tag=tag_name,
                    expanded=expanded,
                    exclusive_predicate=taxonomy_predicate.exclusive,
                    description=taxonomy_entry_of_taxonomy_predicate.description,
                    existing_tag=existing_tag,
                    events=events,
                    attributes=attributes,
                )
            )
    response = GetTagTaxonomyResponse(
        id=taxonomy.id,
        namespace=taxonomy.namespace,
        description=taxonomy.description,
        version=taxonomy.version,
        enabled=taxonomy.enabled,
        exclusive=taxonomy.exclusive,
        required=taxonomy.required,
        highlighted=taxonomy.highlighted,
        entries=taxonomy_entries,
    )
    return response


@alog
async def _export_taxonomy(db: Session, taxonomy_id: int) -> ExportTaxonomyResponse:
    taxonomy: Taxonomy | None = await db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    predicates: list[TaxonomyPredicateSchema] = []
    entries: list[TaxonomyValueSchema] = []

    result = await db.execute(select(TaxonomyPredicate).filter(TaxonomyPredicate.taxonomy_id == taxonomy_id))
    taxonomy_predicates = result.scalars().all()

    for taxonomy_predicate in taxonomy_predicates:
        values: list[ExportTaxonomyEntry] = []
        predicates.append(TaxonomyPredicateSchema(**taxonomy_predicate.__dict__))

        result = await db.execute(
            select(TaxonomyEntry).filter(TaxonomyEntry.taxonomy_predicate_id == taxonomy_predicate.id)
        )
        taxonomy_entries = result.scalars().all()

        for taxonomy_entry in taxonomy_entries:
            values.append(
                ExportTaxonomyEntry(
                    description=taxonomy_entry.description, expanded=taxonomy_entry.expanded, value=taxonomy_entry.value
                )
            )
        value = TaxonomyValueSchema(predicate=taxonomy_predicate.value, entry=values)
        entries.append(value)
    return ExportTaxonomyResponse(
        namespace=taxonomy.namespace,
        description=taxonomy.description,
        version=taxonomy.version,
        exclusive=taxonomy.exclusive,
        predicates=predicates,
        values=entries,
    )


@alog
async def _enable_taxonomy(db: Session, taxonomy_id: int) -> StandardStatusIdentifiedResponse:
    taxonomy: Taxonomy | None = await db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    taxonomy.enabled = True

    await db.flush()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="Taxonomy enabled",
        message="Taxonomy enabled",
        url=f"/taxonomies/enable/{taxonomy_id}",
        id=taxonomy_id,
    )


@alog
async def _disable_taxonomy(db: Session, taxonomy_id: int) -> StandardStatusIdentifiedResponse:
    taxonomy: Taxonomy | None = await db.get(Taxonomy, taxonomy_id)

    if not taxonomy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Taxonomy not found.")

    taxonomy.enabled = False

    await db.flush()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="Taxonomy disabled",
        message="Taxonomy disabled",
        url=f"/taxonomies/disable/{taxonomy_id}",
        id=taxonomy_id,
    )


@alog
async def _get_tag_name(db: Session, taxonomy_entry: TaxonomyEntry) -> str:
    result = await db.execute(
        select(TaxonomyPredicate).filter(TaxonomyPredicate.id == taxonomy_entry.taxonomy_predicate_id).limit(1)
    )
    taxonomy_predicate = result.scalars().one()

    result = await db.execute(select(Taxonomy).filter(Taxonomy.id == taxonomy_predicate.taxonomy_id).limit(1))
    taxonomy = result.scalars().one()

    return str(taxonomy.namespace) + ":" + str(taxonomy_predicate.value) + '="' + str(taxonomy_entry.value) + '"'
