from starlette.routing import Route, Mount
from slut_proxy.models.config import Config

from . import slut

def build_routes(config: Config) -> list[Route | Mount]:
    return [
        Mount("/v2", routes=slut.build_routes(config))
    ]