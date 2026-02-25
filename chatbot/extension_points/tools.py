"""
Extension point: Agent tools (including MCP).

register_agent_tools(agent) is called after the agent is created. By default
it does nothing. To add tools:

1. Custom tools: use @agent.tool in agent.py, or inside register_agent_tools
   register your async functions with the agent.
2. MCP tools: install pydantic-ai[mcp] and use MCPServerStdio / MCPServerHTTP
   to get a toolset, then add it to the agent (see Pydantic AI MCP docs).
"""


def register_agent_tools(agent):
    """
    Register any extra tools or toolsets with the agent. Called once at startup.
    Override this function to add MCP or custom tools.
    """
    pass
