from typing import Self, ClassVar, Any
import msgspec
from msgspec import Struct as MsgStruct
from starlette.requests import Request

from ..utils.responses import MsgspecJSONResponse


class Struct(MsgStruct):
    @classmethod
    async def from_request(cls, request: Request) -> Self:
        body = await request.json()
        return msgspec.json.decode(body, type=cls)

    async def to_response(self, status: int = 200) -> MsgspecJSONResponse:
        return MsgspecJSONResponse(self, status_code=status)


class OpenAIModel(Struct):
    id: str
    owned_by: str
    object: str = "model"
    created: int = 1000166400


class OpenAIResponse(Struct):
    object: str
    data: list[OpenAIModel]


class OpenAICompletionChoice(Struct):
    text: str
    index: int
    finish_reason: str
    logprobs: dict | None = None


class OpenAICompletionUsage(Struct):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAICompletionResponse(Struct):
    id: str
    object: ClassVar[str] = "text_completion"
    created: int
    model: str
    choices: list[OpenAICompletionChoice]
    usage: OpenAICompletionUsage


class OpenAICompletionRequest(Struct, dict=True, kw_only=True):
    model: str
    prompt: str | list[str]
    other_fields: Any
    provider_config: Any
    max_tokens: int | None = None
    
    # Canonical samplers, others are added as dict
    temperature: float | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None

    stop: str | list[str] | None = None
    stream: bool = False

    def __post_init__(self):
        for field in self.__struct_fields__:
            if field in self.other_fields and (field in self.provider_config.supported_parameters or field in self.provider_config.supported_samplers):
                setattr(self, field, self.other_fields[field])
                del self.other_fields[field]
