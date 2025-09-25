from collections.abc import AsyncIterator
import contextlib
from typing import TypedDict

import anyio_sqlite
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .models.config import Config
from .routes import build_routes
from .migrations import do_migration

class State(TypedDict):
    db: anyio_sqlite.Connection  # pyright: ignore[reportMissingTypeArgument]

def build_app(slut_config: Config):
    @contextlib.asynccontextmanager
    async def lifespan(_app) -> AsyncIterator[State]:
        async with anyio_sqlite.connect("slut_proxy.db", isolation_level=None) as con:
            await do_migration(con)
            yield {"db": con}

    app = Starlette(debug=True, routes=build_routes(slut_config), lifespan=lifespan)

    return app