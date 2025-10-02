from collections.abc import Sequence
from starlette.routing import Mount, Route
from slut_proxy.models.config import Config

from . import models, admin, textgen

def build_routes(config: Config) -> Sequence[Route | Mount]:
    return [
        *models.build_routes(config),
        *textgen.build_routes(config),
        *admin.build_routes(config),
    ]