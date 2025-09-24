from starlette.routing import Route
from slut_proxy.models.config import Config

from . import models

def build_routes(config: Config) -> list[Route]:
    return models.build_routes(config)