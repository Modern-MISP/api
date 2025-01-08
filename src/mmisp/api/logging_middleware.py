import logging
from collections.abc import Callable
from typing import Any, Self

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from mmisp.db.database import sessionmanager
from mmisp.lib.logger import print_request_log, reset_db_log, reset_request_log, save_db_log

logger = logging.getLogger("mmisp")


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self: Self, request: Request, call_next: Callable) -> Any:
        # Reset logs for each request
        reset_request_log()
        reset_db_log()
        try:
            # Process the request
            response = await call_next(request)
        except Exception as exc:
            logger.error("Exception occurred", exc_info=True)
            print_request_log()
            raise exc
        else:
            # Emit all logs at the end of the request if no exception
            async with sessionmanager.session() as db:
                await save_db_log(db)
            print_request_log()

        return response
