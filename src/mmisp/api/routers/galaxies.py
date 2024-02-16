from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.galaxies.attach_galaxy_cluster_body import AttachClusterGalaxyBody
from mmisp.api_schemas.galaxies.attach_galaxy_cluster_response import AttachClusterGalaxyResponse
from mmisp.api_schemas.galaxies.delete_force_update_import_galaxy_response import DeleteForceUpdateImportGalaxyResponse
from mmisp.api_schemas.galaxies.export_galaxies_body import ExportGalaxyBody
from mmisp.api_schemas.galaxies.export_galaxies_response import ExportGalaxyResponse
from mmisp.api_schemas.galaxies.get_all_search_galaxies_response import GetAllSearchGalaxiesResponse
from mmisp.api_schemas.galaxies.get_galaxy_response import GetGalaxyResponse
from mmisp.api_schemas.galaxies.import_galaxies_body import ImportGalaxyBody
from mmisp.api_schemas.galaxies.search_galaxies_body import SearchGalaxiesBody
from mmisp.db.database import get_db
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.db.models.tag import Tag
from mmisp.util.partial import partial

router = APIRouter(tags=["galaxies"])


# Sorted according to CRUD

# - Create a {resource}


@router.post(
    "/galaxies/import",
    status_code=status.HTTP_200_OK,
    response_model=partial(DeleteForceUpdateImportGalaxyResponse),
    summary="Add new galaxy cluster",
    description="Add a new galaxy cluster to an existing galaxy.",
)
async def import_galaxy_cluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    body: list[ImportGalaxyBody],
    request: Request,
) -> dict:
    return await _import_galaxy_cluster(db, body, request)


# - Read / Get a {resource}


@router.get("/galaxies/view/{galaxyId}", deprecated=True)  # deprecated
@router.get("/{galaxyId}")  # new
async def galaxies_getBy_id(db: Session = Depends(get_db)) -> GetGalaxyResponse:
    return GetGalaxyResponse()


# - Updating a {resource}


@router.post("/galaxies/update")
async def galaxies_update(db: Session = Depends(get_db)) -> DeleteForceUpdateImportGalaxyResponse:
    return DeleteForceUpdateImportGalaxyResponse


# - Deleting a {resource}


@router.delete("/galaxies/delete/{galaxyId}", deprecated=True)  # deprecated
@router.delete("/galaxies/{galaxyId}")  # new
async def galaxies_delete(galaxy_id: str, db: Session = Depends(get_db)) -> DeleteForceUpdateImportGalaxyResponse:
    return DeleteForceUpdateImportGalaxyResponse()


# - Get all {resource}s


@router.get("/galaxies")
async def galaxies_get(db: Session = Depends(get_db)) -> list[GetAllSearchGalaxiesResponse]:
    return list[GetAllSearchGalaxiesResponse()]


# - More niche endpoints


@router.post("/galaxies")
async def galaxies_post(body: SearchGalaxiesBody, db: Session = Depends(get_db)) -> list[GetAllSearchGalaxiesResponse]:
    return list[GetAllSearchGalaxiesResponse()]


@router.post("/galaxies/export/{galaxyId}")
async def galaxies_export(
    galaxy_id: str, body: ExportGalaxyBody, db: Session = Depends(get_db)
) -> ExportGalaxyResponse:
    return ExportGalaxyResponse()


@router.post("/galaxies/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}")
async def galaxies_attachCluster(
    attachTarget_id: str,
    attachTargetType: str,
    local: int,
    body: AttachClusterGalaxyBody,
    db: Session = Depends(get_db),
) -> AttachClusterGalaxyResponse:
    return AttachClusterGalaxyResponse()


# --- endpoint logic ---


async def _import_galaxy_cluster(
    db: Session, body: list[ImportGalaxyBody], request: Request
) -> DeleteForceUpdateImportGalaxyResponse:
    successfully_imported_counter = 0
    failed_imports_counter = 0

    for element in body:
        element_dict = element.__dict__.copy()
        galaxy_uuid = element_dict["Galaxy"].__dict__.copy()["uuid"]
        galaxy = db.query(Galaxy).filter(Galaxy.uuid == galaxy_uuid)

        galaxy_cluster = element_dict["GalaxyCluster"]
        galaxy_cluster_dict = galaxy_cluster.dict()
        tag_name = element_dict["GalaxyCluster"].__dict__.copy()["tag_name"]
        tag = db.query(Tag).filter(Tag.name == tag_name)

        galaxy_elements = galaxy_cluster_dict["GalaxyElement"]

        if not galaxy:
            failed_imports_counter += 1
        elif not tag:
            failed_imports_counter = +1
        elif galaxy_cluster_dict["default"] is True:
            return DeleteForceUpdateImportGalaxyResponse(
                saved=False,
                name="Could not import Galaxy",
                message="Could not import Galaxy",
                url=str(request.url.path),
                errors=f"Could not import galaxy clusters. {successfully_imported_counter} imported, 0 ignored,"
                f"{failed_imports_counter} failed. Only non-default clusters can be saved",
            )
        else:
            galaxy_cluster_dict["authors"] = " ".join(galaxy_cluster_dict["authors"])

            new_galaxy_cluster = GalaxyCluster(**{**galaxy_cluster_dict})

            try:
                db.add(new_galaxy_cluster)
                db.commit()
            except SQLAlchemyError:
                return DeleteForceUpdateImportGalaxyResponse(
                    name="An Internal Error Has Occurred.",
                    message="An Internal Error Has Occurred.",
                    url=str(request.url.path),
                )
            for galaxy_element in galaxy_elements:
                galaxy_element["galaxy_cluster_id"] = new_galaxy_cluster.id

                del galaxy_element["id"]

                new_galaxy_element = GalaxyElement(**{**galaxy_element})

                print(new_galaxy_element.__dict__.copy())

                try:
                    db.add(new_galaxy_element)
                    db.commit()
                except SQLAlchemyError:
                    return DeleteForceUpdateImportGalaxyResponse(
                        name="An Internal Error Has Occurred.",
                        message="An Internal Error Has Occurred.",
                        url=str(request.url.path),
                    )
        successfully_imported_counter += 1

    if failed_imports_counter > 0:
        return DeleteForceUpdateImportGalaxyResponse(
            saved=False,
            name="Could not import Galaxy",
            message="Could not import Galaxy",
            url=str(request.url.path),
            errors=f"Could not import galaxy clusters. 0 imported, 0 ignored, {failed_imports_counter} failed.",
        )
    return DeleteForceUpdateImportGalaxyResponse(
        saved=True,
        success=True,
        name=f"Galaxy clusters imported. {successfully_imported_counter} imported, 0 ignored, 0 failed.",
        message=f"Galaxy clusters imported. {successfully_imported_counter} imported, 0 ignored, 0 failed.",
        url=str(request.url.path),
    )
