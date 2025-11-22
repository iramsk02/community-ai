import asyncio

from dotenv import load_dotenv
import typer


from state import RuntimeState
import commands


load_dotenv()

state = RuntimeState()

app = typer.Typer(help="GitHub MCP Agent CLI")


@app.command("list-tools")
def list_tools() -> int:
    """List the available MCP tools from the GitHub server."""
    return asyncio.run(commands.list_tools(state))


@app.command("chat")
def chat(
    message: str = typer.Argument(..., help="Message to send to the agent."),
    session_id: str = typer.Option("default", help="Chat session identifier."),
) -> int:
    """Send a message to the agent and stream the response."""
    return asyncio.run(commands.chat(state, message=message, session_id=session_id))


@app.command("chat-loop")
def chat_loop(
    session_id: str = typer.Option(
        "default",
        help="Chat session identifier to use for the loop.",
    ),
    exit_command: str = typer.Option(
        "/exit",
        help="Command typed alone on a line to end the loop.",
    ),
    reset_command: str = typer.Option(
        "/reset",
        help="Command typed alone on a line to reset the session history.",
    ),
    prompt_prefix: str | None = typer.Option(
        None,
        help="Optional custom prompt prefix displayed before user input.",
    ),
) -> int:
    """Start an interactive multi-turn chat session."""
    return asyncio.run(
        commands.chat_loop(
            state,
            session_id=session_id,
            exit_command=exit_command,
            reset_command=reset_command,
            prompt_prefix=prompt_prefix,
        )
    )


@app.command("tool-info")
def tool_info(
    tool_identifier: str = typer.Argument(
        ..., help="Tool CLI or original name."
    )
) -> int:
    """Show detailed information about a tool."""
    return asyncio.run(commands.tool_info(state, tool_identifier=tool_identifier))


@app.command("invoke-tool")
def invoke_tool(
    tool_identifier: str = typer.Argument(
        ..., help="Tool CLI or original name to invoke."
    ),
    args_json: str = typer.Option(
        "{}",
        help="JSON object containing arguments for the tool.",
    ),
) -> int:
    """Invoke a GitHub MCP tool directly."""
    return asyncio.run(
        commands.invoke_tool(
            state,
            tool_identifier=tool_identifier,
            args_json=args_json,
        )
    )


@app.command("sessions")
def sessions() -> int:
    """List active chat session identifiers."""
    return asyncio.run(commands.sessions(state))


@app.command("clear-session")
def clear_session(
    session_id: str = typer.Argument(..., help="Session id to clear."),
) -> int:
    """Clear a stored chat session."""
    return asyncio.run(commands.clear_session(state, session_id=session_id))


@app.command("export-session")
def export_session(
    session_id: str = typer.Argument(
        ..., help="Session id to export."
    ),
    output_path: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional path to write the exported JSON transcript.",
    ),
) -> int:
    """Export a chat session transcript for testing or archival."""
    return asyncio.run(
        commands.export_session(
            state,
            session_id=session_id,
            output_path=output_path,
        )
    )


@app.command("health")
def health() -> int:
    """Show initialization status and tool count."""
    return asyncio.run(commands.health(state))


if __name__ == "__main__":
    app()
