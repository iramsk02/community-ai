from lib import base_commands
from lib.state import RuntimeState
from github.agent import get_github_agent


__all__ = [
    "list_tools",
    "tool_info",
    "invoke_tool",
    "chat",
    "chat_loop",
    "sessions",
    "clear_session",
    "export_session",
    "health",
]


_github_agent = get_github_agent()


async def list_tools(state: RuntimeState) -> int:
    return await base_commands.list_tools(state, _github_agent)


async def tool_info(state: RuntimeState, tool_identifier: str) -> int:
    return await base_commands.tool_info(state, _github_agent, tool_identifier)


async def invoke_tool(
    state: RuntimeState,
    tool_identifier: str,
    args_json: str | None = None,
) -> int:
    return await base_commands.invoke_tool(
        state, _github_agent, tool_identifier, args_json
    )


async def chat(
    state: RuntimeState,
    message: str,
    session_id: str = "default",
) -> int:
    return await base_commands.chat(state, _github_agent, message, session_id)


async def chat_loop(
    state: RuntimeState,
    session_id: str = "default",
    exit_command: str = "/exit",
    reset_command: str = "/reset",
    prompt_prefix: str | None = None,
) -> int:
    return await base_commands.chat_loop(
        state,
        _github_agent,
        session_id,
        exit_command,
        reset_command,
        prompt_prefix,
    )


async def sessions(state: RuntimeState) -> int:
    return await base_commands.sessions(state)


async def clear_session(state: RuntimeState, session_id: str) -> int:
    return await base_commands.clear_session(state, session_id)


async def export_session(
    state: RuntimeState,
    session_id: str,
    output_path: str | None = None,
) -> int:
    return await base_commands.export_session(state, session_id, output_path)


async def health(state: RuntimeState) -> int:
    return await base_commands.health(state)
