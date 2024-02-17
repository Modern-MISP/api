from typing import Type, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

T = TypeVar("T")


def check_existence_and_raise(
    db: Session, model: Type[T], value: str, column_name: str = "id", error_detail: str = "Resource not found."
) -> T:
    """
    Checks if a resource exists in the database based on the given model and value for a specified column.
    Throws an HTTPException if the resource is not found.

    Args:
    - db: Database session
    - model: Database model class to search for
    - value: Value of the column to search for
    - column_name: Name of the column for search purposes (default is 'id')
    - error_detail: Detail message for the HTTPException

    Returns:
    - Found resource of type `model`
    """
    resource = db.query(model).filter(getattr(model, column_name) == value).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_detail)
    return resource
