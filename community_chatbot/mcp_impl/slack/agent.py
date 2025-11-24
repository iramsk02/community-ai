import os
from typing import Any
from lib.base_agent import BaseAgent

__all__ = [
    "get_slack_agent",
]


def get_slack_agent() -> BaseAgent:
    """
    Create and configure a Slack MCP agent.
    
    Supports multiple authentication modes:
    - XOXP (OAuth token): Recommended, more secure
    - XOXC/XOXD (Browser tokens): Stealth mode, no additional permissions
    
    Supports multiple transports:
    - stdio: Default, runs server as subprocess (npx slack-mcp-server@latest)
    - sse: Server-Sent Events, connects to separate running server
    - streamable_http: HTTP transport for remote servers
    """
    
    # Check for authentication tokens
    has_xoxp = bool(os.getenv("SLACK_MCP_XOXP_TOKEN"))
    has_xoxc = bool(os.getenv("SLACK_MCP_XOXC_TOKEN"))
    has_xoxd = bool(os.getenv("SLACK_MCP_XOXD_TOKEN"))
    
    # Validate authentication
    if not has_xoxp and not (has_xoxc and has_xoxd):
        required_vars = [
            "SLACK_MCP_XOXP_TOKEN or (SLACK_MCP_XOXC_TOKEN and SLACK_MCP_XOXD_TOKEN)"
        ]
    else:
        required_vars = []
    
    # Determine transport and connection configuration
    transport = os.getenv("SLACK_MCP_TRANSPORT", "stdio").lower()
    
    if transport == "stdio":
        # stdio transport: Run npx slack-mcp-server as subprocess
        return _create_stdio_agent(required_vars)
    elif transport in ("sse", "streamable_http"):
        # SSE/HTTP transport: Connect to running server
        return _create_http_agent(required_vars, transport)
    else:
        raise ValueError(
            f"Unsupported SLACK_MCP_TRANSPORT: {transport}. "
            f"Supported values: 'stdio', 'sse', 'streamable_http'"
        )


def _create_stdio_agent(required_vars: list[str]) -> BaseAgent:
    """Create Slack agent with stdio transport (npx subprocess)."""
    
    class SlackStdioAgent(BaseAgent):
        def get_connection_config(self) -> dict[str, Any]:
            """Build stdio connection config for local slack-mcp-server."""
            # Pass authentication tokens to the server
            env_vars = {
                "PATH": os.environ.get("PATH", ""),
                "SLACK_MCP_XOXP_TOKEN": os.getenv(
                    "SLACK_MCP_XOXP_TOKEN", ""
                ),
                "SLACK_MCP_XOXC_TOKEN": os.getenv(
                    "SLACK_MCP_XOXC_TOKEN", ""
                ),
                "SLACK_MCP_XOXD_TOKEN": os.getenv(
                    "SLACK_MCP_XOXD_TOKEN", ""
                ),
                "SLACK_MCP_ADD_MESSAGE_TOOL": os.getenv(
                    "SLACK_MCP_ADD_MESSAGE_TOOL", ""
                ),
            }
            
            # Use local node_modules binary (installed via package.json)
            import pathlib
            project_root = pathlib.Path(__file__).parent.parent
            local_bin = (
                project_root / "node_modules" / ".bin"
                / "slack-mcp-server.cmd"
            )
            
            return {
                "transport": "stdio",
                "command": str(local_bin),
                "args": ["--transport", "stdio"],
                "env": env_vars,
            }
    
    return SlackStdioAgent(
        service_name="slack",
        required_env_vars=required_vars,
    )


def _create_http_agent(required_vars: list[str], transport: str) -> BaseAgent:
    """Create Slack agent with SSE/HTTP transport."""
    
    class SlackHttpAgent(BaseAgent):
        def __init__(self, transport_type: str, **kwargs):
            super().__init__(**kwargs)
            self.transport_type = transport_type
        
        def validate_environment(self) -> None:
            """Validate environment for HTTP/SSE transport."""
            super().validate_environment()
            
            # For HTTP/SSE, we need server URL
            if not os.getenv("SLACK_MCP_SERVER_URL"):
                raise ValueError(
                    "SLACK_MCP_SERVER_URL is required for SSE/HTTP transport. "
                    "Example: http://127.0.0.1:13080/sse"
                )
        
        def get_connection_config(self) -> dict[str, Any]:
            """Build HTTP/SSE connection config."""
            from lib.utils import build_connection_config
            
            server_url = os.getenv("SLACK_MCP_SERVER_URL", "http://127.0.0.1:13080/sse")
            
            # Build base config
            config = build_connection_config(
                service_name="slack",
                server_url_env="SLACK_MCP_SERVER_URL",
                default_server_url=server_url,
                token_env=None,  # Not used for HTTP/SSE
                bearer_token_env="SLACK_MCP_API_KEY",
            )
            
            # Override transport if using SSE
            if self.transport_type == "sse":
                config["transport"] = "sse"
            
            return config
    
    return SlackHttpAgent(
        transport_type=transport,
        service_name="slack",
        required_env_vars=required_vars,
    )
