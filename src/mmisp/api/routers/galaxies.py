import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.galaxies.delete_force_update_import_galaxy_response import DeleteForceUpdateImportGalaxyResponse
from mmisp.api_schemas.galaxies.export_galaxies_response import ExportGalaxyClusterResponse, ExportGalaxyGalaxyElement
from mmisp.api_schemas.galaxies.get_all_search_galaxies_response import (
    GetAllSearchGalaxiesAttributes,
)
from mmisp.api_schemas.galaxies.get_galaxy_response import GetGalaxyResponse
from mmisp.api_schemas.galaxies.import_galaxies_body import ImportGalaxyBody
from mmisp.db.database import get_db
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.db.models.tag import Tag
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["galaxies"])
logging.basicConfig(level=logging.INFO)

info_format = "%(asctime)s - %(message)s"
error_format = "%(asctime)s - %(filename)s:%(lineno)d - %(message)s"

info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(info_format))

error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(error_format))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(info_handler)
logger.addHandler(error_handler)


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
@router.get("/galaxies/{galaxyId}", status_code=status.HTTP_200_OK, response_model=partial(GetGalaxyResponse))  # new
async def get_galaxy_details(
    db: Annotated[Session, Depends(get_db)], galaxy_id: Annotated[str, Path(..., alias="galaxyId")]
) -> dict:
    return await _get_galaxy_details(db, galaxy_id)


# - Updating a {resource}


# @router.post("/galaxies/update")
# async def galaxies_update(db: Session = Depends(get_db)) -> DeleteForceUpdateImportGalaxyResponse:
#     return DeleteForceUpdateImportGalaxyResponse()


# - Deleting a {resource}


@router.delete("/galaxies/delete/{galaxyId}", deprecated=True)  # deprecated
@router.delete(
    "/galaxies/{galaxyId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(DeleteForceUpdateImportGalaxyResponse),
)  # new
async def galaxies_delete(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(..., alias="galaxyId")],
    request: Request,
) -> DeleteForceUpdateImportGalaxyResponse:
    return await _delete_galaxy(db, galaxy_id, request)


# - Get all {resource}s


# @router.get("/galaxies")
# async def galaxies_get(db: Session = Depends(get_db)) -> list[GetAllSearchGalaxiesResponse]:
#     return list[GetAllSearchGalaxiesResponse()]
#
#
# # - More niche endpoints
#
#
# @router.post("/galaxies")
# async def galaxies_post(body: SearchGalaxiesBody, db: Session = Depends(get_db))
# -> list[GetAllSearchGalaxiesResponse]:
#     return list[GetAllSearchGalaxiesResponse()]
#
#
# @router.post("/galaxies/export/{galaxyId}")
# async def galaxies_export(
#         galaxy_id: str, body: ExportGalaxyBody, db: Session = Depends(get_db)
# ) -> ExportGalaxyClusterResponse:
#     return ExportGalaxyClusterResponse()
#
#
# @router.post("/galaxies/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}")
# async def galaxies_attachCluster(
#         attachTarget_id: str,
#         attachTargetType: str,
#         local: int,
#         body: AttachClusterGalaxyBody,
#         db: Session = Depends(get_db),
# ) -> AttachClusterGalaxyResponse:
#     return AttachClusterGalaxyResponse()


# --- endpoint logic ---


async def _import_galaxy_cluster(
    db: Session, body: list[ImportGalaxyBody], request: Request
) -> DeleteForceUpdateImportGalaxyResponse:
    successfully_imported_counter = 0
    failed_imports_counter = 0

    for element in body:
        element_dict = element.__dict__.copy()

        galaxy_cluster = element_dict["GalaxyCluster"]
        galaxy_cluster_dict = galaxy_cluster.dict()

        galaxy_elements = galaxy_cluster_dict["GalaxyElement"]

        galaxy_cluster_type = galaxy_cluster_dict["type"]

        galaxies_with_given_type = db.query(Galaxy).filter(Galaxy.type == galaxy_cluster_type).all()

        if galaxy_cluster_dict["default"] is True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=DeleteForceUpdateImportGalaxyResponse(
                    saved=False,
                    name="Could not import Galaxy",
                    message="Could not import Galaxy",
                    url=str(request.url.path),
                    errors=f"Could not import galaxy clusters. {successfully_imported_counter} imported, 0 ignored,"
                    f"{failed_imports_counter} failed. Only non-default clusters can be saved",
                ).dict(),
            )
        elif len(galaxies_with_given_type) == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=DeleteForceUpdateImportGalaxyResponse(
                    saved=False,
                    name="Could not import Galaxy",
                    message="Could not import Galaxy",
                    url=str(request.url.path),
                    errors=f"Could not import galaxy clusters. {successfully_imported_counter} imported, 0 ignored,"
                    f"{failed_imports_counter} failed. Galaxy not found",
                ).dict(),
            )
        else:
            galaxy_cluster_dict["authors"] = " ".join(galaxy_cluster_dict["authors"])
            del galaxy_cluster_dict["GalaxyElement"]

            # fields_to_convert = ["galaxy_id", "version", "distribution", "sharing_group_id", "org_id", "orgc_id",
            #                      "extends_version"]
            # for field in fields_to_convert:
            #     if galaxy_cluster_dict.get(field) is not None:
            #         galaxy_cluster_dict[field] = int(galaxy_cluster_dict[field])
            #     else:
            #         galaxy_cluster_dict[field] = 1

            # ** {**galaxy_cluster_dict, "galaxy_id": int(galaxy_cluster.galaxy_id),
            #     "version": int(galaxy_cluster.version),
            #     "distribution": int(galaxy_cluster.distribution),
            #     "sharing_group_id": int(galaxy_cluster.sharing_group_id),
            #     "org_id": int(galaxy_cluster.org_id),
            #     "orgc_id": int(galaxy_cluster.orgc_id),
            #     "extends_version": int(galaxy_cluster.extends_version)}

            # version = int(galaxy_cluster.version),
            # distribution = galaxy_cluster.distribution,
            # sharing_group_id = galaxy_cluster.sharing_group_id,
            # org_id = galaxy_cluster.org_id, orgc_id = galaxy_cluster.orgc_id,
            # default = galaxy_cluster.default, locked = galaxy_cluster.locked,
            # extends_uuid = galaxy_cluster.extends_uuid,
            # extends_version = int(galaxy_cluster.extends_version),
            # published = galaxy_cluster.published, deleted = galaxy_cluster.deleted

            new_galaxy_cluster = GalaxyCluster(
                type=galaxy_cluster.type,
                value=galaxy_cluster.value,
                tag_name=galaxy_cluster.tag_name,
                description=galaxy_cluster.description,
                galaxy_id=galaxy_cluster.galaxy_id,
                source=galaxy_cluster.source,
                authors=" ".join(galaxy_cluster.authors),
            )

            logger.info(new_galaxy_cluster.__dict__.copy())

            try:
                db.add(new_galaxy_cluster)
                db.commit()
            except SQLAlchemyError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=DeleteForceUpdateImportGalaxyResponse(
                        name="An Internal Error Has Occurred.",
                        message="An Internal Error Has Occurred.",
                        url=str(request.url.path),
                    ).dict(),
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
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=DeleteForceUpdateImportGalaxyResponse(
                            name="An Internal Error Has Occurred.",
                            message="An Internal Error Has Occurred.",
                            url=str(request.url.path),
                        ).dict(),
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


async def _get_galaxy_details(db: Session, galaxy_id: str) -> dict:
    galaxy = check_existence_and_raise(db, Galaxy, galaxy_id, "galaxy_id", "Galaxy not found")

    galaxy_data = _prepare_galaxy_response(db, galaxy)
    galaxy_cluster_data = _prepare_galaxy_cluster_response(db, galaxy)

    return GetGalaxyResponse(Galaxy=galaxy_data, GalaxyCluster=galaxy_cluster_data)


async def _delete_galaxy(db: Session, galaxy_id: str, request: Request) -> DeleteForceUpdateImportGalaxyResponse:
    galaxy = db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteForceUpdateImportGalaxyResponse(
                saved=False, success=False, name="Invalid galaxy.", message="Invalid galaxy.", url=str(request.url.path)
            ).dict(),
        )
    connected_tag_name = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).first().tag_name
    connected_tag = db.query(Tag).filter(Tag.name == connected_tag_name).first()

    db.delete(galaxy)
    db.delete(connected_tag)
    db.commit()

    # galaxy = db.get(Galaxy, galaxy_id)

    return DeleteForceUpdateImportGalaxyResponse(
        saved=True, success=True, name="Galaxy deleted", message="Galaxy deleted", url=str(request.url.path)
    )


def _prepare_galaxy_response(db: Session, galaxy: Galaxy) -> GetAllSearchGalaxiesAttributes:
    galaxy_dict = galaxy.__dict__.copy()
    galaxy_cluster = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).first()
    tag = db.query(Tag).filter(Tag.name == galaxy_cluster.tag_name).first()
    galaxy_dict["local_only"] = tag.local_only

    return GetAllSearchGalaxiesAttributes(**galaxy_dict)


def _prepare_galaxy_cluster_response(db: Session, galaxy: Galaxy) -> list[ExportGalaxyClusterResponse]:
    response_list = []

    galaxy_cluster_list = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).all()

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

            galaxy_element_list = (
                db.query(GalaxyElement).filter(GalaxyElement.galaxy_cluster_id == galaxy_cluster.id).all()
            )
            galaxy_cluster_dict["GalaxyElement"] = []

            if len(galaxy_element_list) > 0:
                for galaxy_element in galaxy_element_list:
                    galaxy_element_dict = galaxy_element.__dict__.copy()
                    galaxy_cluster_dict["GalaxyElement"].append(ExportGalaxyGalaxyElement(**galaxy_element_dict))

            response_list.append(ExportGalaxyClusterResponse(**galaxy_cluster_dict))

    return response_list
