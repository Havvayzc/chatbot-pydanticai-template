"""
Extension point: System prompt and model selection.

Change DEFAULT_SYSTEM_PROMPT and DEFAULT_MODEL here to adapt the chatbot's
personality and which LLM provider/model it uses. You can also load these
from environment variables or a config file for different environments.
"""

# Default instructions sent to the model as the "system" role. This shapes
# how the assistant responds (tone, scope, rules).
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant. "
    "Answer concisely and clearly. If you don't know something, say so."
)

# Model identifier: "provider:model-name". Examples:
#   - openai:gpt-4o-mini
#   - anthropic:claude-sonnet-4
#   - openai:gpt-4o
# Set OPENAI_API_KEY, ANTHROPIC_API_KEY, etc. in your environment as needed.
DEFAULT_MODEL = "openai:gpt-4o-mini"
