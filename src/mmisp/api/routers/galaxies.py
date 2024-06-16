from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.future import select
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.events import (
    AddEditGetEventGalaxyClusterRelation,
    AddEditGetEventGalaxyClusterRelationTag,
    GetAllEventsGalaxyClusterGalaxy,
)
from mmisp.api_schemas.galaxies import (
    AttachClusterGalaxyBody,
    AttachClusterGalaxyResponse,
    DeleteForceUpdateImportGalaxyResponse,
    ExportGalaxyBody,
    ExportGalaxyClusterResponse,
    ExportGalaxyGalaxyElement,
    GetAllSearchGalaxiesAttributes,
    GetAllSearchGalaxiesResponse,
    GetGalaxyClusterResponse,
    GetGalaxyResponse,
    ImportGalaxyBody,
    SearchGalaxiesbyValue,
)
from mmisp.api_schemas.organisations import Organisation as OrganisationSchema
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventTag
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag

router = APIRouter(tags=["galaxies"])




@router.get("/galaxies/{galaxyId}", status_code=status.HTTP_200_OK, response_model=GetGalaxyResponse)
async def get_galaxy_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
) -> GetGalaxyResponse:
    """"Gets the details of a galaxy."""
    return await _get_galaxy_details(db, galaxy_id)


@router.post(
    "/galaxies/update",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=DeleteForceUpdateImportGalaxyResponse,
    summary="Update galaxies",
)
async def update_galaxy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.WORKER_KEY, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> DeleteForceUpdateImportGalaxyResponse:
    """Force the galaxies to update with the JSON definitions, not yet implemented."""
    raise NotImplementedError()


#    return DeleteForceUpdateImportGalaxyResponse()


@router.delete(
    "/galaxies/{galaxyId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteForceUpdateImportGalaxyResponse,
    summary="Delete a galaxy",
)
async def delete_galaxy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
    request: Request,
) -> DeleteForceUpdateImportGalaxyResponse:
    """"Delete a specific galaxy by its Id."""
    return await _delete_galaxy(db, galaxy_id, request)


@router.get(
    "/galaxies",
    status_code=status.HTTP_200_OK,
    response_model=list[GetAllSearchGalaxiesResponse],
    summary="Get all galaxies",
)
async def get_galaxies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> list[GetAllSearchGalaxiesResponse]:
    """Get a list with all existing galaxies."""
    return await _get_galaxies(db)


@router.post(
    "/galaxies",
    status_code=status.HTTP_200_OK,
    response_model=list[GetAllSearchGalaxiesResponse],
    summary="Search galaxies",
)
async def search_galaxies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchGalaxiesbyValue,
) -> list[GetAllSearchGalaxiesResponse]:
    """Search galaxies by search term which matches with galaxy name, namespace, description, kill_chain_order or uuid."""
    return await _search_galaxies(db, body)




# --- deprecated ---


@router.get(
    "/galaxies/view/{galaxyId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=GetGalaxyResponse,
    summary="View Galaxy by ID.",
)
async def get_galaxy_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
) -> GetGalaxyResponse:
    """View Galaxy by given Galaxy ID."""
    return await _get_galaxy_details(db, galaxy_id)


@router.delete(
    "/galaxies/delete/{galaxyId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=DeleteForceUpdateImportGalaxyResponse,
    summary="Delete Galaxy by ID",
)
async def delete_galaxy_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
    request: Request,
) -> DeleteForceUpdateImportGalaxyResponse:
    """Delete Galaxy by GalaxyID."""
    return await _delete_galaxy(db, galaxy_id, request)


# --- endpoint logic ---




async def _get_galaxy_details(db: Session, galaxy_id: str) -> GetGalaxyResponse:
    galaxy: Galaxy | None = await db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    galaxy_data = await _prepare_galaxy_response(db, galaxy)
    galaxy_cluster_data = await _prepare_galaxy_cluster_response(db, galaxy)

    return GetGalaxyResponse(Galaxy=galaxy_data, GalaxyCluster=galaxy_cluster_data)

async def _prepare_galaxy_response(db: Session, galaxy: Galaxy) -> GetAllSearchGalaxiesAttributes:
    galaxy_dict = galaxy.__dict__.copy()

    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).limit(1))
    galaxy_cluster = result.scalars().first()

    if galaxy_cluster is None:
        galaxy_dict["local_only"] = True

    return GetAllSearchGalaxiesAttributes(**galaxy_dict)

async def _prepare_galaxy_cluster_response(db: Session, galaxy: Galaxy) -> list[GetGalaxyClusterResponse]:
    response_list = []

    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id))
    galaxy_cluster_list = result.scalars().all()

    if len(galaxy_cluster_list) > 0:
        for galaxy_cluster in galaxy_cluster_list:
            galaxy_cluster_dict = galaxy_cluster.__dict__.copy()

            galaxy_cluster_dict["authors"] = galaxy_cluster_dict["authors"].split(" ")

            int_fields_to_convert = ["sharing_group_id", "org_id", "orgc_id", "extends_version"]
            for field in int_fields_to_convert:
                if galaxy_cluster_dict.get(field) is not None:
                    galaxy_cluster_dict[field] = str(galaxy_cluster_dict[field])
                else:
                    galaxy_cluster_dict[field] = "0"

            if galaxy_cluster_dict.get("collection_uuid") is None:
                galaxy_cluster_dict["collection_uuid"] = ""
            if galaxy_cluster_dict.get("extends_uuid") is None:
                galaxy_cluster_dict["extends_uuid"] = ""
            if galaxy_cluster_dict.get("distribution") is None:
                galaxy_cluster_dict["distribution"] = "0"
            else:
                galaxy_cluster_dict["distribution"] = str(galaxy_cluster_dict["distribution"])

            bool_fields_to_convert = ["default", "locked", "published", "deleted"]
            for field in bool_fields_to_convert:
                if galaxy_cluster_dict.get(field) is None:
                    galaxy_cluster_dict[field] = False

            result = await db.execute(
                select(GalaxyElement).filter(GalaxyElement.galaxy_cluster_id == galaxy_cluster.id)
            )
            galaxy_element_list = result.scalars().all()
            galaxy_cluster_dict["GalaxyElement"] = []

            if len(galaxy_element_list) > 0:
                for galaxy_element in galaxy_element_list:
                    galaxy_element_dict = galaxy_element.__dict__.copy()
                    galaxy_cluster_dict["GalaxyElement"].append(ExportGalaxyGalaxyElement(**galaxy_element_dict))

            response_list.append(GetGalaxyClusterResponse(**galaxy_cluster_dict))

    return response_list


async def _delete_galaxy(db: Session, galaxy_id: str, request: Request) -> DeleteForceUpdateImportGalaxyResponse:
    galaxy = await db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteForceUpdateImportGalaxyResponse(
                saved=False, success=False, name="Invalid galaxy.", message="Invalid galaxy.", url=str(request.url.path)
            ).dict(),
        )

    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).limit(1))
    connected_tag_name = result.scalars().one().tag_name

    result = await db.execute(select(Tag).filter(Tag.name == connected_tag_name))
    connected_tag = result.scalars().first()

    await db.delete(galaxy)
    await db.delete(connected_tag)
    await db.commit()

    return DeleteForceUpdateImportGalaxyResponse(
        saved=True, success=True, name="Galaxy deleted", message="Galaxy deleted", url=str(request.url.path)
    )


async def _get_galaxies(db: Session) -> list[GetAllSearchGalaxiesResponse]:
    result = await db.execute(select(Galaxy))
    galaxies = result.scalars().all()
    response_list = []

    if not galaxies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No galaxies found.")

    for galaxy in galaxies:
        response_list.append(GetAllSearchGalaxiesResponse(Galaxy=await _prepare_galaxy_response(db, galaxy)))

    return response_list


async def _search_galaxies(db: Session, body: SearchGalaxiesbyValue) -> list[GetAllSearchGalaxiesResponse]:
    search_term = body.value
    result = await db.execute(
        select(Galaxy).filter(
            Galaxy.name.contains(search_term),
            Galaxy.namespace.contains(search_term),
            Galaxy.description.contains(search_term),
            Galaxy.kill_chain_order.contains(search_term),
            Galaxy.uuid.contains(search_term),
        )
    )
    galaxies: Sequence[Galaxy] = result.scalars().all()

    response_list = []

    for galaxy in galaxies:
        galaxy_dict = galaxy.__dict__
        response_list.append(GetAllSearchGalaxiesResponse(Galaxy=GetAllSearchGalaxiesAttributes(**galaxy_dict)))

    return response_list

