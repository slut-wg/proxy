from typing import Self
from enum import Enum
import msgspec
from msgspec import Struct as MsgStruct
from starlette.requests import Request

from ..utils.responses import MsgspecJSONResponse
from .config import AvailableSampler, ModelConfig, ProviderConfig

class Struct(MsgStruct):
    @classmethod
    async def from_request(cls, request: Request) -> Self:
        body = await request.json()
        return msgspec.json.decode(body, type=cls)

    async def to_response(self, status: int = 200) -> MsgspecJSONResponse:
        return MsgspecJSONResponse(self, status_code=status)


class ModelMetadata(Struct):
    """
    Describes the metadata response type of a specific model
    """

    name: str
    provider: str
    supported_parameters: list[str]
    supported_samplers: list[AvailableSampler]

    @classmethod
    def from_model_config(cls, model: ModelConfig, provider: ProviderConfig) -> Self:
        return cls(
            name = model.name,
            provider = model.provider,
            supported_parameters = model.supported_parameters if model.supported_parameters else provider.supported_parameters,
            supported_samplers = model.supported_samplers if model.supported_samplers else provider.supported_samplers,
        )

class StopReason(Enum):
    END_OF_GENERATION = "end_of_generation_reached"
    MAX_TOKENS = "max_tokens_reached"
    ERROR = "error"

class Samplers(Struct):
    temperature: float | None = None
    top_p: float | None = None
    min_p: float | None = None
    repetition_penalty: float | None = None

class TextGenerationRequest(Struct):
    prompt: str | list[int]
    model: str
    samplers: Samplers | None = None
    stop_sequences: list[str | int | list[int]] | None = None

class TextGenerationResponse(Struct):
    text: str
    stop_reason: StopReason

class NewChunkEvent(Struct):
    text: str

class ApiKeyInfo(Struct):
    key: str
    allowed_providers: list[str]
    allowed_models: list[str]

class ApiKeyReq(Struct):
    key: str

