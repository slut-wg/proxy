# 🌸 SLUT Proxy Server

A cute and powerful reference implementation of the SLUT (Simple LLM Unified Transmission) protocol! This proxy server acts as a unified interface between your applications and multiple LLM providers.

## What is this?

The SLUT Proxy is a Python-based server that implements the SLUT protocol specification. It allows you to:

- Talk to multiple LLM providers through one consistent API
- Handle authentication and API key management
- Get OpenAI compatibility for existing integrations
- Enjoy streaming text generation with proper error handling

## Features

- 🎀 **Multi-Provider Support**: OpenAI, Anthropic, and more!
- 🚀 **High Performance**: Async/await with FastAPI-like routing
- 🔐 **Built-in Auth**: API key management and access control
- 📊 **Admin Dashboard**: Web interface for monitoring and management
- 🔄 **OpenAI Compatible**: Drop-in replacement for OpenAI API
- 🌊 **Streaming Support**: Real-time text generation via SSE

## Quick Start

### Installation

```bash
# Clone and install dependencies
cd proxy
uv sync
```

### Configuration

Create a `config.toml` file:

```toml
[proxy]
admin_key = "your-secret-admin-key"
host = "0.0.0.0"
port = 8000

[providers.openai]
base_url = "https://api.openai.com/v1"
api_key = "sk-your-openai-key"
default_models = ["gpt-4", "gpt-3.5-turbo"]

[providers.anthropic]
base_url = "https://api.anthropic.com"
api_key = "sk-ant-your-anthropic-key"
default_models = ["claude-3-sonnet", "claude-3-haiku"]
```

### Running the Server

```bash
uv run src/slut_proxy/main.py
```

The server will start on `http://localhost:8000`!

## API Endpoints

### SLUT Protocol (`/v2`)

- `GET /v2/models` - List all available models
- `GET /v2/models/{model_name}` - Get specific model info
- `POST /v2/generate` - Generate text (sync or streaming)
- `GET /v2/admin` - Admin dashboard
- `GET /v2/admin/api_keys` - List API keys
- `POST /v2/admin/api_keys` - Create new API key
- `DELETE /v2/admin/api_keys` - Delete API key

### OpenAI Compatibility (`/v1`)

- `GET /v1/models` - Models in OpenAI format
- `POST /v1/completions` - Completions in OpenAI format

## Usage Examples

### Generate Text (Sync)

```bash
curl -X POST "http://localhost:8000/v2/generate" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "prompt": "Once upon a time",
    "samplers": {
      "temperature": 0.7,
      "top_p": 0.95
    }
  }'
```

### Generate Text (Streaming)

```bash
curl -X POST "http://localhost:8000/v2/generate" \
  -H "Authorization: Bearer your-api-key" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "prompt": "Write a poem about"
  }'
```

### Admin Dashboard

Visit `http://localhost:8000/v2/admin` in your browser (requires admin key in query params).

## Architecture

The proxy is built with:

- **Starlette** for the web framework
- **msgspec** for fast JSON serialization
- **anyio-sqlite** for database operations
- **TypeSpec** for API specification compliance

## Configuration Options

See `src/slut_proxy/models/config.py` for all available configuration options.

## Development

### Running Tests

```bash
uv run pytest
```

### Code Style

```bash
uv run ruff check
uv run ruff format
```

## License

This implementation is licensed under the AGPLv3.

## Contributing

We welcome contributions! Please check out our [main SLUT working group](https://github.com/slut-wg) for guidelines.

---

*Built with 💕 by the [allura.moe](https://allura.moe/) community*
