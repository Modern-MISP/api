from typing import Callable, Self

from fastapi import FastAPI, Request, Response
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from pyinstrument.renderers.speedscope import SpeedscopeRenderer


class ProfileMiddleware:
    def __init__(self: Self, app: FastAPI, profiling_enabled: bool) -> None:
        self.app = app
        self.profiling_enabled = profiling_enabled
        self.profile_type_to_ext = {"html": "html", "speedscope": "speedscope.json"}
        self.profile_type_to_renderer = {
            "html": HTMLRenderer,
            "speedscope": SpeedscopeRenderer,
        }

    async def __call__(self: Self, request: Request, call_next: Callable) -> Response:  # type: ignore
        # If profiling is enabled and 'profile' query parameter is passed
        if self.profiling_enabled and request.query_params.get("profile", False):
            profile_type = request.query_params.get("profile_format", "speedscope")
            renderer_class = self.profile_type_to_renderer.get(profile_type)

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
