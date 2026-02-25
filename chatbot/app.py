"""
FastAPI/Starlette application using the official Pydantic AI Chat UI.

The UI is the React-based [@pydantic/ai-chat-ui](https://github.com/pydantic/ai-chat-ui),
built on the Vercel AI SDK. By default it is loaded from the CDN and cached locally.
Conversations are stored in the browser (localStorage); for server-side memory
see chatbot/memory.py and the extension points in the README.

To customize models or tools shown in the UI, edit the `agent.to_web(...)` call
below or add optional config in chatbot/config.py.
"""

from __future__ import annotations

# Optional: enable observability with Pydantic Logfire (no-op if not installed).
try:
    import logfire

    logfire.configure(send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()
except ImportError:
    pass

from chatbot.agent import agent

# Create the web app using the official Pydantic AI Chat UI.
# - Default: UI is fetched from CDN (https://cdn.jsdelivr.net/npm/@pydantic/ai-chat-ui) and cached.
# - To use a local build: pass html_source=Path("static/ai-chat-ui/index.html") after building the UI.
# - models: optional dict of display name -> model id for the model selector (agent's model is always included).
# - builtin_tools: optional list (e.g. [WebSearchTool(), CodeExecutionTool()]) to expose in the UI.
app = agent.to_web(
    models={
        "GPT-4o mini": "openai:gpt-4o-mini",
        # Add more models as needed, e.g. "Claude Sonnet": "anthropic:claude-sonnet-4",
    },
    builtin_tools=[],  # Extension point: add e.g. WebSearchTool(), CodeExecutionTool() from pydantic_ai.builtin_tools
)

# Optional: instrument the app for Logfire (if installed with starlette extra).
try:
    import logfire

    logfire.instrument_starlette(app)
except (ImportError, RuntimeError):
    pass

# Run with: uv run uvicorn chatbot.app:app --reload
# Then open http://localhost:8000
