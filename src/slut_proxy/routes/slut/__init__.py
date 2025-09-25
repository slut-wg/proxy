from collections.abc import Sequence
from starlette.routing import Mount, Route
from slut_proxy.models.config import Config

from . import models

def build_routes(config: Config) -> Sequence[Route | Mount]:
    return models.build_routes(config)