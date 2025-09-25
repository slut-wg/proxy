from starlette.requests import Request
from starlette.routing import Mount, Route

from slut_proxy.models.slut import ModelMetadata
from slut_proxy.models.config import Config
from slut_proxy.utils.responses import MsgspecJSONResponse

def build_routes(config: Config) -> list[Mount]:
    def create_api_key(request: Request):
        return MsgspecJSONResponse({"success": True})

    def get_api_key(request: Request):
        return MsgspecJSONResponse({"response": "stub"})
    
    def list_api_keys(request: Request):
        return MsgspecJSONResponse({"response": "stub"})
    
    def delete_api_key(request: Request):
        return MsgspecJSONResponse({"response": "stub"})

    routes = [
        Route("/api_keys", get_api_key, methods=["GET"]),
        Route("/api_keys", delete_api_key, methods=["DELETE"]),
        Route("/api_keys", create_api_key, methods=["POST"]),
        Route("/api_keys/list", list_api_keys, methods=["GET"]),
    ]

    return [
        Mount("/v2/admin", routes=routes)
    ]