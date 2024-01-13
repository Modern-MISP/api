from fastapi import APIRouter


router = APIRouter(tags=["jobs"])


@router.get("/jobs/{id}")
async def start_login(id: str) -> dict:
    return {}
