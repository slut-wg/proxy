import json
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from slut_proxy.models.slut import TextGenerationRequest
from slut_proxy.models.config import Config
from slut_proxy.providers.factory import create_provider

def build_routes(config: Config) -> list[Route]:
    async def generate(request: Request) -> JSONResponse | StreamingResponse:
        """Handle text generation requests (both sync and streaming)"""
        accept_header = request.headers.get("accept", "application/json")
        
        # Parse request body
        body = await request.json()
        gen_request = TextGenerationRequest(**body)
        
        # Get model and provider config
        model_config = config.get_model(gen_request.model)
        provider_config = config.get_provider(model_config.provider)
        
        # Check API key permissions
        api_permissions = getattr(request.state, 'api_key_permissions', None)
        if not api_permissions:
            return JSONResponse(
                {"error": "No API key permissions found"},
                status_code=403
            )
        
        # Better permission handling: 
        # - If model is allowed but provider is not -> allow (200)
        # - If model isn't explicitly allowed but provider is -> allow (200) 
        # - If neither are allowed -> unauthorized (403)
        model_allowed = gen_request.model in api_permissions["allowed_models"]
        provider_allowed = model_config.provider in api_permissions["allowed_providers"]
        
        if not model_allowed and not provider_allowed:
            return JSONResponse(
                {"error": f"Neither model {gen_request.model} nor provider {model_config.provider} are allowed for this API key"},
                status_code=403
            )
        
        # Create provider instance and generate response
        async with create_provider(provider_config) as provider:
            stream = "text/event-stream" in accept_header
            return await provider.generate(model_config, gen_request, stream=stream)

    
    return [
        Route("/generate", generate, methods=["POST"])
    ]
