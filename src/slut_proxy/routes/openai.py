import time
import uuid
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from slut_proxy.models.compat import (
    OpenAIModel, OpenAIResponse, OpenAICompletionRequest, 
    OpenAICompletionResponse, OpenAICompletionChoice, OpenAICompletionUsage
)
from slut_proxy.models.slut import TextGenerationRequest, Samplers
from slut_proxy.models.config import Config
from slut_proxy.utils.responses import MsgspecJSONResponse
from slut_proxy.providers.factory import create_provider

def build_routes(config: Config) -> list[Route]:
    async def get_models(request: Request) -> MsgspecJSONResponse:
        """Get models in OpenAI format"""
        openai_models = []
        
        for model in config.models:
            provider_config = config.get_provider(model.provider)
            openai_model = OpenAIModel(
                id=model.name,
                owned_by=provider_config.name
            )
            openai_models.append(openai_model)
        
        response = OpenAIResponse(
            object="list",
            data=openai_models
        )
        
        return MsgspecJSONResponse(response)

    async def create_completion(request: Request) -> JSONResponse | StreamingResponse:
        """Create completion in OpenAI format"""
        body = await request.json()
        
        # Get model and provider config
        model_config = config.get_model(body["model"])
        provider_config = config.get_provider(model_config.provider)

        completion_request = OpenAICompletionRequest(model=body["model"], prompt=body["prompt"], other_fields=body, provider_config=provider_config)
        
        # Check API key permissions
        api_permissions = getattr(request.state, 'api_key_permissions', None)
        if not api_permissions:
            return JSONResponse(
                {"error": {"message": "No API key permissions found", "type": "invalid_request_error"}},
                status_code=403
            )
        
        # Better permission handling: 
        # - If model is allowed but provider is not -> allow (200)
        # - If model isn't explicitly allowed but provider is -> allow (200) 
        # - If neither are allowed -> unauthorized (403)
        model_allowed = completion_request.model in api_permissions["allowed_models"]
        provider_allowed = model_config.provider in api_permissions["allowed_providers"]
        
        if not model_allowed and not provider_allowed:
            return JSONResponse(
                {"error": {"message": f"Neither model {completion_request.model} nor provider {model_config.provider} are allowed for this API key", "type": "invalid_request_error"}},
                status_code=403
            )
        
        # Convert OpenAI request to internal TextGenerationRequest
        samplers = Samplers()
        if completion_request.temperature is not None:
            samplers.temperature = completion_request.temperature
        if completion_request.top_p is not None:
            samplers.top_p = completion_request.top_p
        
        # Handle prompt (convert list of prompts to first one)
        prompt_text = completion_request.prompt
        if isinstance(prompt_text, list):
            prompt_text = prompt_text[0]
        
        # Handle stop sequences
        stop_sequences = None
        if completion_request.stop:
            if isinstance(completion_request.stop, str):
                stop_sequences = [completion_request.stop]
            else:
                stop_sequences = completion_request.stop
        
        gen_request = TextGenerationRequest(
            prompt=prompt_text,
            model=completion_request.model,
            samplers=samplers if any([samplers.temperature, samplers.top_p]) else None,
            stop_sequences=stop_sequences
        )
        
        # Create provider instance and generate response
        async with create_provider(provider_config) as provider:
            if completion_request.stream:
                return await _stream_completion(provider, model_config, gen_request, completion_request)
            else:
                return await _create_completion_response(provider, model_config, gen_request, completion_request)

    async def _create_completion_response(provider, model_config, gen_request, completion_request):
        """Generate non-streaming completion response"""
        response = await provider.generate(model_config, gen_request, stream=False)
        
        # Convert internal response to OpenAI format
        choice = OpenAICompletionChoice(
            text=response._content.text,
            index=0,
            finish_reason=response._content.stop_reason.value
        )
        
        # Simple token estimation (you may want to improve this)
        prompt_tokens = len(gen_request.prompt.split()) if isinstance(gen_request.prompt, str) else len(str(gen_request.prompt))
        completion_tokens = len(response._content.text.split())
        
        usage = OpenAICompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )
        
        completion_response = OpenAICompletionResponse(
            id=f"cmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=completion_request.model,
            choices=[choice],
            usage=usage
        )
        
        return MsgspecJSONResponse(completion_response)

    async def _stream_completion(provider, model_config, gen_request, completion_request):
        """Generate streaming completion response"""
        completion_id = f"cmpl-{uuid.uuid4().hex[:8]}"
        created = int(time.time())
        
        async def stream_generator():
            async for chunk in provider.generate(model_config, gen_request, stream=True):
                if chunk.text:
                    choice = OpenAICompletionChoice(
                        text=chunk.text,
                        index=0,
                        finish_reason=""
                    )
                    
                    stream_response = {
                        "id": completion_id,
                        "object": "text_completion",
                        "created": created,
                        "model": completion_request.model,
                        "choices": [choice]
                    }
                    
                    yield f"data: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created))}\n"
                    yield f"data: {stream_response}\n\n"
            
            # Send final chunk
            final_choice = OpenAICompletionChoice(
                text="",
                index=0,
                finish_reason="stop"
            )
            
            final_response = {
                "id": completion_id,
                "object": "text_completion", 
                "created": created,
                "model": completion_request.model,
                "choices": [final_choice]
            }
            
            yield f"data: {final_response}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(stream_generator(), media_type="text/plain")

    return [
        Route("/models", get_models, methods=["GET"]),
        Route("/completions", create_completion, methods=["POST"])
    ]
