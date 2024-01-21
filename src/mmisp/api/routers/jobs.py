from fastapi import APIRouter

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{id}")
async def get_job(id: str) -> dict:
    return {}
