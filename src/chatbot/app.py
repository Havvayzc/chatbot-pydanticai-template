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

from chatbot.agent import agent
from chatbot.config import get_litellm_supported_models, use_litellm

# Models to show in the UI. When using LiteLLM, the agent's model is the only one.
_web_models = get_litellm_supported_models() if use_litellm() else {"GPT-4o mini": "openai:gpt-4o-mini"}

# Create the web app using the official Pydantic AI Chat UI.
# - Default: UI is fetched from CDN (@pydantic/ai-chat-ui) and cached.
# - To use a local build: pass html_source=Path("static/ai-chat-ui/index.html") after building.
# - models: optional dict of display name -> model id (agent's model is always included).
# - builtin_tools: optional list (e.g. [WebSearchTool(), CodeExecutionTool()]) to expose in the UI.
app = agent.to_web(
    models=_web_models,
    builtin_tools=[],
)


# Run with: uv run uvicorn chatbot.app:app --reload
# Then open http://localhost:8000
