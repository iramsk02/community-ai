import os
from typing import Any, cast

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from state import RuntimeState
from utils import (
    build_connection_config,
    sanitize_tool_name,
    schema_from_model,
)


__all__ = [
    "initialize_agent",
    "ensure_agent_initialized",
    "stream_agent_response",
]


def _get_llm_provider():

    provider = os.getenv("LLM_PROVIDER", "lightning").lower()
    
    if provider == "lightning":
        from lightning_llm import get_llm
    elif provider == "groq":
        from groq_llm import get_llm
    elif provider == "gemini":
        from gemini import get_llm
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {provider}. "
            f"Supported values: 'lightning', 'groq', 'gemini'"
        )
    
    return get_llm


async def initialize_agent(state: RuntimeState) -> None:
    missing_vars: list[str] = []
    if not (
        os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        or os.getenv("GITHUB_MCP_BEARER_TOKEN")
    ):
        missing_vars.append("GITHUB_PERSONAL_ACCESS_TOKEN")

    if missing_vars:
        missing_str = ", ".join(sorted(set(missing_vars)))
        raise ValueError(
            "Missing required environment variables: " + missing_str
        )

    connection = build_connection_config()

    state.mcp_client = MultiServerMCPClient({"github": connection})

    client = state.mcp_client
    if client is None:
        raise RuntimeError("Failed to initialize MCP client.")

    # Get tools from MCP client - no server_name parameter needed
    tools = await client.get_tools()

    state.tool_summaries = []
    state.tool_map = {}
    state.tool_details = {}

    for tool in tools:
        original_name = tool.name
        sanitized_name = sanitize_tool_name(original_name)

        args_schema = schema_from_model(getattr(tool, "args_schema", None))
        metadata = getattr(tool, "metadata", {}) or {}

        state.tool_map[sanitized_name] = tool
        state.tool_details[sanitized_name] = {
            "name": sanitized_name,
            "original_name": original_name,
            "description": getattr(tool, "description", ""),
            "metadata": metadata,
            "args_schema": args_schema,
        }
        state.tool_summaries.append(
            {
                "name": sanitized_name,
                "original_name": original_name,
                "description": getattr(tool, "description", ""),
            }
        )

    # Get LLM and create agent with tools
    get_llm = _get_llm_provider()
    llm = get_llm()
    
    # Create React agent with model and tools
    # The agent will automatically bind tools to the model
    state.agent_executor = create_react_agent(llm, tools)


async def ensure_agent_initialized(state: RuntimeState) -> None:
    if state.agent_executor is None or state.mcp_client is None:
        await initialize_agent(state)
    if state.agent_executor is None or state.mcp_client is None:
        raise RuntimeError("Agent failed to initialize")


async def stream_agent_response(
    state: RuntimeState,
    session_history: list[BaseMessage],
) -> AIMessage:
    if state.agent_executor is None:
        raise RuntimeError("Agent executor is not initialized.")

    executor = cast(Any, state.agent_executor)
    
    # Use ainvoke for async execution with the agent
    result = await executor.ainvoke({"messages": session_history})
    
    # Extract the last AI message from the result
    messages = result.get("messages", [])
    last_ai_message: AIMessage | None = None
    
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            last_ai_message = message
            break
    
    if last_ai_message is None:
        raise RuntimeError("The agent did not return a response.")
    return last_ai_message
