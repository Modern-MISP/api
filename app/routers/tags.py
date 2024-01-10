from typing import List

from fastapi import APIRouter, Depends  # , HTTPException
from sqlalchemy.orm import Session

from ..database import get_db

# from ..models.tag import Tag
from ..schemas.tags.tag_schema import TagDeleteSchema, TagSchema, TagSearchSchema

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagSchema])
async def get_tags(db: Session = Depends(get_db)) -> None:
    pass


@router.get("/view/{tagId}", response_model=List[TagSchema])
@router.get("/{tagId}", response_model=List[TagSchema])
async def view_tag(tag_id: str, db: Session = Depends(get_db)) -> None:
    pass


@router.post("/add", response_model=List[TagSchema])
@router.post("/", response_model=List[TagSchema])
async def add_tag(db: Session = Depends(get_db)) -> None:
    pass


@router.delete("/delete/{tagId}", response_model=List[TagDeleteSchema])
@router.delete("/{tagId}", response_model=List[TagDeleteSchema])
async def delete_tag(tag_id: str, db: Session = Depends(get_db)) -> None:
    pass


@router.post("/edit/{tagId}", response_model=List[TagSchema])
@router.put("/{tagId}", response_model=List[TagSchema])
async def edit_tag(tag_id: str, db: Session = Depends(get_db)) -> None:
    pass


@router.get("search/{tagSearchTerm}", response_model=List[TagSearchSchema])
async def search_tags(tagSearchTerm: str, db: Session = Depends(get_db)) -> None:
    pass
