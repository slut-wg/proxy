import json
from typing import Dict, Any, Union
import httpx
from starlette.responses import JSONResponse, StreamingResponse

from . import BaseProvider
from ..models.config import ProviderConfig, ModelConfig
from ..models.slut import TextGenerationRequest, TextGenerationResponse, StopReason
from ..utils.responses import MsgspecJSONResponse


class OpenAIProvider(BaseProvider):
    async def generate(
        self, 
        model_config: ModelConfig,
        request: TextGenerationRequest,
        stream: bool = False
    ) -> Union[TextGenerationResponse, StreamingResponse]:
        provider_request = self.prepare_request(model_config, request)
        
        if stream:
            return await self._handle_streaming_response(provider_request)
        else:
            return await self._handle_sync_response(provider_request)
    
    def prepare_request(
        self, 
        model_config: ModelConfig,
        request: TextGenerationRequest
    ) -> Dict[str, Any]:
        provider_request = {
            "model": model_config.model_id,
            "prompt": request.prompt,
        }
        
        if request.samplers:
            if "temperature" in request.samplers:
                provider_request["temperature"] = request.samplers["temperature"]
            if "top_p" in request.samplers:
                provider_request["top_p"] = request.samplers["top_p"]
            if "min_p" in request.samplers:
                provider_request["min_p"] = request.samplers.min_p
            if "repetition_penalty" in request.samplers:
                provider_request["repetition_penalty"] = request.samplers.repetition_penalty
        
        if request.stop_sequences:
            provider_request["stop"] = request.stop_sequences
        
        return provider_request
    
    def parse_response(
        self, 
        response_data: Dict[str, Any]
    ) -> TextGenerationResponse:
        text = response_data.get("choices", [{}])[0].get("text", "")
        
        finish_reason = response_data.get("choices", [{}])[0].get("finish_reason", "stop")
        if finish_reason == "length":
            stop_reason = StopReason.MAX_TOKENS
        elif finish_reason == "stop":
            stop_reason = StopReason.END_OF_GENERATION
        else:
            stop_reason = StopReason.ERROR
        
        return TextGenerationResponse(text=text, stop_reason=stop_reason)
    
    async def _handle_sync_response(
        self, 
        provider_request: Dict[str, Any]
    ) -> MsgspecJSONResponse:
        response = await self.client.post(
            f"{self.config.base_url}/completions",
            json=provider_request,
            headers=self._get_auth_headers()
        )
        response.raise_for_status()
        
        provider_data = response.json()
        result = self.parse_response(provider_data)
        return MsgspecJSONResponse(result)
    
    async def _handle_streaming_response(
        self, 
        provider_request: Dict[str, Any]
    ) -> StreamingResponse:
        provider_request["stream"] = True
        
        async def generate_stream():
            async with self.client.stream(
                "POST",
                f"{self.config.base_url}/completions",
                json=provider_request,
                headers=self._get_auth_headers()
            ) as response:
                response.raise_for_status()
                
                accumulated_text = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            final_event = {
                                "event": "done",
                                "data": json.dumps({
                                    "text": accumulated_text,
                                    "stop_reason": "end_of_generation_reached"
                                })
                            }
                            yield f"event: {final_event['event']}\ndata: {final_event['data']}\n\n"
                            break
                        
                        try:
                            chunk_data = json.loads(data)
                            if "choices" in chunk_data and chunk_data["choices"]:
                                delta = chunk_data["choices"][0].get("text", "")
                                if delta:
                                    accumulated_text += delta
                                    chunk_event = {
                                        "event": "new_chunk",
                                        "data": json.dumps({"text": delta})
                                    }
                                    yield f"event: {chunk_event['event']}\ndata: {chunk_event['data']}\n\n"
                        except json.JSONDecodeError:
                            continue
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )