from typing import Callable, Self

from fastapi import FastAPI, Request, Response
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from pyinstrument.renderers.speedscope import SpeedscopeRenderer
from starlette.middleware.base import BaseHTTPMiddleware


class ProfileMiddleware(BaseHTTPMiddleware):
    def __init__(self: Self, app: FastAPI) -> None:
        super().__init__(app)
        self.profile_type_to_ext = {"html": "html", "speedscope": "speedscope.json"}
        self.profile_type_to_renderer = {
            "html": HTMLRenderer,
            "speedscope": SpeedscopeRenderer,
        }

    async def dispatch(self: Self, request: Request, call_next: Callable) -> Response:  # type: ignore
        # If profiling is enabled and 'profile' query parameter is passed
        if request.query_params.get("profile", False):
            profile_type = request.query_params.get("profile_format", "speedscope")
            renderer_class = self.profile_type_to_renderer.get(profile_type)
            assert renderer_class is not None

            with Profiler(interval=0.001, async_mode="enabled") as profiler:
                response = await call_next(request)

            # Write profile to file
            extension = self.profile_type_to_ext[profile_type]
            renderer = renderer_class()
            with open(f"profile.{extension}", "w") as out_file:
                out_file.write(profiler.output(renderer=renderer))

            return response

        # Proceed without profiling
        return await call_next(request)
