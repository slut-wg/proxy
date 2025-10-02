from . import BaseProvider
from .openai import OpenAIProvider

def create_provider(config):
    if config.type.value == "openai":
        return OpenAIProvider(config)
    else:
        raise ValueError(f"Unsupported provider type: {config.type}")