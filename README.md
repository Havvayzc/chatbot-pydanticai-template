# chatbot-pydanticai-template

A minimal template for building a **custom chatbot** with [Pydantic AI](https://ai.pydantic.dev/) and the official **[Pydantic AI Chat UI](https://github.com/pydantic/ai-chat-ui)** (React + Vercel AI SDK), with clear **extension points** for students.

## Features

- **Pydantic AI agent** – type-safe, model-agnostic agent with configurable system prompt and model.
- **Official Pydantic AI Chat UI** – React-based chat interface ([ai-chat-ui](https://github.com/pydantic/ai-chat-ui)) with streaming, tool visualization, model selector, and dark/light theme. Loaded from CDN by default.
- **Streaming API** – `agent.to_web()` exposes the Vercel AI Data Stream protocol at `/api/chat` and `/api/configure`.
- **Extension points** – config (prompt/model), tools (including MCP), vector store placeholder, and conversational memory (see `chatbot/memory.py` for server-side persistence if you build a custom UI).

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip  
- An API key for your chosen model (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).

## Quick start

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install dependencies
uv sync

# Set your API key, then run the app
export OPENAI_API_KEY=sk-...
uv run uvicorn chatbot.app:app --reload
```

Open **http://localhost:8000** – the Pydantic AI Chat UI loads from the CDN on first use and is cached locally.

## Project layout

| Path | Purpose |
|------|--------|
| `chatbot/config.py` | **Extension point:** system prompt and model selection |
| `chatbot/agent.py` | Pydantic AI agent creation and tool registration |
| `chatbot/app.py` | Starlette app via `agent.to_web()` – serves the [ai-chat-ui](https://github.com/pydantic/ai-chat-ui) and `/api` |
| `chatbot/memory.py` | **Extension point:** server-side conversational memory (SQLite); used if you add a custom UI or adapter |
| `chatbot/extension_points/tools.py` | **Extension point:** add tools (e.g. MCP) to the agent |
| `chatbot/extension_points/vector_store.py` | **Extension point:** RAG / vector search placeholder |
| `static/` | Optional: previous simple HTML/JS UI (see `static/README.md`); not used when running `agent.to_web()` |

## Extension points (for students)

### 1. System prompt and model

Edit **`chatbot/config.py`**:

- `DEFAULT_SYSTEM_PROMPT` – instructions that define the assistant’s behaviour.
- `DEFAULT_MODEL` – e.g. `openai:gpt-4o-mini`, `anthropic:claude-sonnet-4`.

You can also load these from environment variables or a config file.

### 2. Conversational memory

Default behaviour is in **`chatbot/memory.py`**: a SQLite store that persists messages under `.chat_messages.sqlite`.

To change the backend (e.g. Redis, PostgreSQL, or in-memory for tests), replace the `ChatMemory` implementation or the logic that calls `get_messages()` / `add_messages()` so it uses your store. The default **Pydantic AI Chat UI** keeps conversations in the browser (localStorage). To use server-side memory, integrate `ChatMemory` into a custom route that uses `VercelAIAdapter` and passes `message_history` from your store (see [Pydantic AI message history](https://ai.pydantic.dev/message-history/)).

### 3. Vector store (RAG)

**`chatbot/extension_points/vector_store.py`** is a placeholder. To add retrieval-augmented generation:

1. Add a dependency (e.g. `chromadb`, `qdrant-client`) in `pyproject.toml`.
2. Implement `retrieve(query, top_k)` (or similar) to return relevant chunks.
3. Use that context in the agent (e.g. via dynamic `@agent.instructions` or by prepending context to the user message).

### 4. MCP tools

**`chatbot/extension_points/tools.py`** exposes `register_agent_tools(agent)`. By default it does nothing.

To add tools:

- **Custom tools:** use the `@agent.tool` decorator (see Pydantic AI [tools docs](https://ai.pydantic.dev/tools/)) or register callables inside `register_agent_tools(agent)`.
- **MCP:** install `pydantic-ai[mcp]` and connect to an MCP server (e.g. `MCPServerStdio`), then attach the returned toolset to the agent in `register_agent_tools`.

## Optional dependencies

```bash
# Observability (Pydantic Logfire; no-op if not configured)
uv sync --extra logfire

# MCP client support
uv sync --extra mcp
```

## Code comments

The code is commented so students can follow:

- How the agent is built and where instructions/model come from.
- How the streaming response is generated and how messages are serialized.
- Where to plug in a different memory backend, vector store, or tools.

## Licence

See [LICENSE](LICENSE).
