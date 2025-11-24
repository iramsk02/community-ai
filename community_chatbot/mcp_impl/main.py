import sys
from pathlib import Path

import typer
from github import github_mcp
from slack import slack_mcp

sys.path.insert(0, str(Path(__file__).parent))


app = typer.Typer(
    help="Community AI MCP Agent - Unified access to GitHub, Slack, and more"
)

app.add_typer(
    github_mcp.app,
    name="github",
    help="GitHub MCP Agent - Interact with GitHub repositories"
)

app.add_typer(
    slack_mcp.app,
    name="slack",
    help="Slack MCP Agent - Interact with Slack workspaces"
)


if __name__ == "__main__":
    app()
