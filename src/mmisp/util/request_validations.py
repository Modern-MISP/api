import logging
from typing import List, Optional, Type, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

T = TypeVar("T")  # Generic type for database models


def check_existence_and_raise(
    db: Session,
    model: Type[T],
    identifier: str,
    identifier_name: str = "id",
    error_detail: str = "Not found error",
    log_error: Optional[str] = None,
) -> None:
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


def check_required_fields(body: object, required_fields: List[str]) -> None:
    """
    Checks if required fields are present and not empty in the body.
    Throws an HTTPException if a required field is missing.

    Args:
    - body: Body object with data
    - required_fields: List of required field names
    """
    for field in required_fields:
        if not str(getattr(body, field, None)):
            logging.error(f"Object creation failed: field '{field}' is required.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{field}' is required.")
