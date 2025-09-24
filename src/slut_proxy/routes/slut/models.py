from starlette.requests import Request
from starlette.routing import Route

from slut_proxy.models.slut import ModelMetadata
from slut_proxy.models.config import Config
from slut_proxy.utils.responses import MsgspecJSONResponse

def build_routes(config: Config) -> list[Route]:
    def list_models(_request: Request) -> MsgspecJSONResponse:
        metadatas = []
        for model in config.models:
            metadatas.append(ModelMetadata.from_model_config(model, config.get_provider(model.provider)) )  # pyright: ignore[reportUnknownMemberType]
        return MsgspecJSONResponse(metadatas)
    
    def get_model(request: Request) -> MsgspecJSONResponse:
        model_name: str = request.path_params["model"]
        model_config = config.get_model(model_name)
        provider_config = config.get_provider(model_config.provider)
        return MsgspecJSONResponse(ModelMetadata.from_model_config(model_config, provider_config))


    return [
        Route("/models", list_models),
        Route("/models/{model}", get_model)
    ]