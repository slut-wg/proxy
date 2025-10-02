from abc import ABC, abstractmethod
from typing import Dict, Any, Union
import httpx
from starlette.responses import JSONResponse, StreamingResponse

from ..models.config import ProviderConfig, ModelConfig
from ..models.slut import TextGenerationRequest, TextGenerationResponse, StopReason


class BaseProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = httpx.AsyncClient()
    
    @abstractmethod
    async def generate(
        self, 
        model_config: ModelConfig,
        request: TextGenerationRequest,
        stream: bool = False
    ) -> Union[TextGenerationResponse, StreamingResponse]:
        pass
    
    @abstractmethod
    def prepare_request(
        self, 
        model_config: ModelConfig,
        request: TextGenerationRequest
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def parse_response(
        self, 
        response_data: Dict[str, Any]
    ) -> TextGenerationResponse:
        pass
    
    def _get_auth_headers(self) -> Dict[str, str]:
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()