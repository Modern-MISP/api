from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .error import LegacyMISPCompatibleHTTPException


def legacy_misp_exception_handler(request: Any, exc: LegacyMISPCompatibleHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"message": exc.message})


def not_implemented_exception_handler(request: Any, exc: NotImplementedError) -> JSONResponse:
    return JSONResponse(status_code=501, content={"message": str(exc)})


def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(LegacyMISPCompatibleHTTPException, legacy_misp_exception_handler)
    app.add_exception_handler(NotImplementedError, not_implemented_exception_handler)
