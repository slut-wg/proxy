from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .models.config import Config

from .routes import build_routes

def build_app(slut_config: Config):
    async def index(_request: Request):
        return JSONResponse({"hai": ":3"})

    app = Starlette(debug=True, routes=build_routes(slut_config))

    return app
