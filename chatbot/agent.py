"""
Pydantic AI agent setup.

The agent is created from config (system prompt, model). Optional tools from
extension_points (e.g. MCP, custom tools) are registered after creation so
the model can call them during the conversation.
"""

from chatbot.config import DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT
from chatbot.extension_points.tools import register_agent_tools
from pydantic_ai import Agent

# Build the agent with instructions and model from config.
# To use a different model per request, pass model=... to agent.run_stream().
agent = Agent(
    DEFAULT_MODEL,
    instructions=DEFAULT_SYSTEM_PROMPT,
)

# Extension point: register tools (e.g. MCP tools). By default this does nothing;
# override register_agent_tools() in extension_points/tools.py to add tools.
register_agent_tools(agent)
