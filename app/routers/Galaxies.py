from pydantic import BaseModel
from typing import List
from fastapi import APIRouter


class Galaxies(BaseModel):
    id: str = ""
    uuid: str = ""
    name: str = ""
    type: str = ""
    description: str = ""
    version: str = ""
    icon: str = ""
    namespace: str = ""
    kill_chain_order: List[str] = [""]


router = APIRouter(prefix="/galaxies")


@router.get("/galaxies")
async def galaxies_get():
    return


@router.post("/galaxies")
async def galaxies_post():
    return


@router.get("/galaxies/view/{galaxyId}")
@router.get("/galaxies/{galaxyId}")
async def galaxies_getById():
    return


@router.post("/galaxies/update")
async def galaxies_update():
    return


@router.delete("/galaxies/delete/{galaxyId}")
@router.delete("/galaxies/{galaxyId}")
async def galaxies_delete():
    return


@router.post("/galaxies/import")
async def galaxies_import():
    return


@router.post("/galaxies/export/{galaxyId}")
async def galaxies_export():
    return


@router.post(
    "/galaxies/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}"
)
async def galaxies_attachCluster():
    return
