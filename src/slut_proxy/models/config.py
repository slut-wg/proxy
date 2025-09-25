from enum import Enum
from typing import Self
import msgspec
from msgspec import Struct

class AvailableProvider(Enum):
    OPENAI_COMPATIBLE = "openai"
    ANTHROPIC_COMPATIBLE = "anthropic"
    LLAMA_CPP = "llama.cpp"
    KOBOLDCPP = "kobold.cpp"

class AvailableSampler(Enum):
    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    MIN_P = "min_p"
    REP_PEN = "repetition_penalty"

class ProviderConfig(Struct):
    name: str
    type: AvailableProvider

    base_url: str
    api_key: str | None = None

    # The following are optional and will only be used if models do not have their own specific configs
    supported_parameters: list[str] = []
    supported_samplers: list[AvailableSampler] = []

class ModelConfig(Struct):
    name: str # what is served
    model_id: str # what is requested on the provider
    provider: str # correlates to the provider name from above, NOT the provider type

    supported_parameters: list[str] | None = None
    supported_samplers: list[AvailableSampler] | None = None

class ProxyConfig(Struct):
    admin_key: str

class Config(Struct):
    proxy: ProxyConfig
    providers: list[ProviderConfig]
    models: list[ModelConfig]

    @classmethod
    def from_toml(cls, filename: str) -> Self:
        return msgspec.toml.decode(open(filename).read(-1), type=cls)

    def get_model(self, name: str) -> ModelConfig:
        for model in self.models:
            if model.name == name:
                return model
        raise Exception(f"Model {name} does not exist!")

    def get_provider(self, name: str) -> ProviderConfig:
        for provider in self.providers:
            if provider.name == name:
                return provider
        raise Exception(f"Provider {name} does not exist!")
