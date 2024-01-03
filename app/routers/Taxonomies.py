from pydantic import BaseModel
from typing import List, Annotated
from fastapi import APIRouter

class Taxonomies(BaseModel):
    id: str = ""
    namespace: str = ""
    description: str = ""
    version: str = ""
    enabled: bool
    exclusive: bool
    required: bool
    highlighted: bool

router = APIRouter(prefix="/taxonomies")

#Returns all taxonomies
@router.get("/")
async def get_taxonomies():
    return {
        Taxonomies(),
        {
            "total_count": int,
            "current_count": int
        }
    }

#Get Taxonomy by ID (deprecated)
@router.get("/view/{taxonomy_id_parameter}")
async def get_taxonomy_by_id_depr():
    return {
        Taxonomies(),
        {
            "tag": str,
            "expanded": str,
            "description": str,
            "exclusive_predicate": bool,
            "existing_tag": bool
        }
    }

#Get Taxonomy by ID (new)
@router.get("/{taxonomy_id_parameter}")
async def get_taxonomy_by_id():
    return{
        Taxonomies(),
        {
            "tag": str,
            "expanded": str,
            "description": str,
            "exclusive_predicate": bool,
            "existing_tag": bool
        }
    }

#Enable Taxonomy
@router.post("/enable/{taxonomiesId}")
async def enable_taxonomies():
    return {
        "id": str,
        "saved": bool,
        "success": bool,
        "name": str,
        "message": str,
        "url": str
    }

#Disable Taxonomies
@router.post("/disable/{taxonomiesId}")
async def disable_taxonomies():
    return {
        "id": str,
        "saved": bool,
        "success": bool,
        "name": str,
        "message": str,
        "url": str
    }

#Update Taxonomies. Deprecated
@router.post("/taxonomies/update")
async def update_taxonomies_depr():
    return {
        "saved": bool,
        "success": bool,
        "name": str,
        "message": str,
        "url": str
    }

#Update Taxonomies. New
@router.put("/taxonomies")
async def update_taxonomies():
    return {
        "saved": bool,
        "success": bool,
        "name": str,
        "message": str,
        "url": str
    }

#Get a Taxonomy extended with Tags used in events and attributes
@router.get("/taxonomy_tags/{taxonomyId}")
async def get_taxonomy_extanded():
    return {Taxonomies(),
            {
                "tag": str,
                "expanded": str,
                "exclusive_predicate": bool,
                "description": str,
                "existing_tag": str,
                "server_id": str,
                "email": str,
                "autoalert": bool,
                "authkey": str,
                "invited_by": str,
                "gpgkey": str,
                "certif_public": str,
                "nids_sid": str,
                "termsaccepted": bool,
                "newsread": str,
                "role_id": str,
                "change_pw": str,
                "contactalert": bool,
                "disabled": bool,
                "expiration": str,
                "current_login": str,
                "last_login": str,
                "force_logout": bool,
                "date_created": str,
                "date_modified": str,
                "events": int,
                "attributes": int
            }}
