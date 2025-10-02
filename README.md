# 🌸 SLUT Proxy Server

A cute and powerful reference implementation of the SLUT (Simple LLM Unified Transmission) protocol! This proxy server acts as a unified interface between your applications and multiple LLM providers.

## What is this?

The SLUT Proxy is a Python-based server that implements the SLUT protocol specification. It allows you to:

- Talk to multiple LLM providers through one consistent API
- Handle authentication and API key management
- Get OpenAI compatibility for existing integrations
- Enjoy streaming text generation with proper error handling

## Features

- 🎀 **Multi-Provider Support**: Supports any OpenAI-compatible endpoint, with more coming soon!
- 🔐 **Built-in Auth**: API key management and access control
- 📊 **Admin Dashboard**: Web interface for monitoring and management
- 🔄 **OpenAI Compatible**: Drop-in replacement for OpenAI API
- 🌊 **(Untested) Streaming Support**: Real-time text generation via SSE

## Quick Start

### Installation

```bash
# Clone and install dependencies
cd proxy
uv sync
```

### Configuration

Create a `config.toml` file, for example with Openrouter:

```toml
[proxy]
admin_key = "test"

[[providers]]
name = "openrouter"
type = "openai"
base_url = "https://openrouter.ai/api/v1"
api_key = "xyz"

supported_parameters = ["stop_sequences", "seed"]

[[models]]
name = "Seed OSS 36B Instruct"
model_id = "bytedance/seed-oss-36b-instruct"
provider = "openrouter"

supported_samplers = ["temperature", "top_p", "min_p", "repetition_penalty"]

```

### Running the Server

```bash
uv run src/slut_proxy/main.py
```

The server will start on `http://localhost:8080`!

## API Endpoints

Docs are TODO! Please see [the spec](https://github.com/slut-wg/proxy) for now.

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

Visit `http://localhost:8080/v2/admin` in your browser.

## Architecture

The proxy is built with:

- **Starlette** for the web framework
- **msgspec** for fast JSON serialization & structs
- **anyio-sqlite** for database operations
- **TypeSpec** for API specification compliance

## Configuration Options

See `src/slut_proxy/models/config.py` for all available configuration options.

## License

This implementation is licensed under the AGPLv3.

## Contributing

We welcome contributions! Please check out our [main SLUT working group](https://github.com/slut-wg) for guidelines.

---

*Built with 💕 by the [allura.moe](https://allura.moe/) community*
