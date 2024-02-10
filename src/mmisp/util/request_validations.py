import logging
from typing import Optional, Type, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

T = TypeVar("T")


def check_existence_and_raise(
    db: Session,
    model: Type[T],
    identifier: str,
    identifier_name: str = "id",
    error_detail: str = "Not found error",
    log_error: Optional[str] = None,
) -> T:
    """
    Checks if an object exists in the database based on the given model and identifier.
    Throws an HTTPException if the object is not found.

    Args:
    - db: Database session
    - model: Database model class to search for
    - identifier: Value of the identifier to search for
    - identifier_name: Name of the identifier for logging purposes (default is 'id')
    - error_detail: Detail message for the HTTPException
    - log_error: Optional, specific error message for logging

    Returns:
    - Found object of type `model`
    """
    obj = db.get(model, identifier)
    if not obj:
        log_msg = log_error if log_error else f"{model.__name__} with {identifier_name} '{identifier}' not found."
        logging.error(log_msg)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_detail)
    return obj
