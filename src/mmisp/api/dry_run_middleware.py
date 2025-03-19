import logging
from collections.abc import Callable
from typing import Any, Self

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from mmisp.db.database import dry_run

logger = logging.getLogger("mmisp")


class DryRunMiddleware(BaseHTTPMiddleware):
    async def dispatch(self: Self, request: Request, call_next: Callable) -> Any:
        if request.query_params.get("dry_run", False):
            logger.info("Doing a dry-run request")
            dry_run.set(True)

        return await call_next(request)
