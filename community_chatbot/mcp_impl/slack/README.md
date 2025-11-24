# Info on Transport Configuration

## Option 1: stdio Transport (Default - Recommended for Getting Started)

Runs the Slack MCP server as a subprocess using npx.

**Configuration** (`.env`):
```env
SLACK_MCP_TRANSPORT=stdio
# Authentication tokens (see above)
SLACK_MCP_XOXP_TOKEN=xoxp-your-token-here
```

**Requirements**:
- Node.js and npx installed
- Internet connection (to download slack-mcp-server@latest)

**How it works**:
- Agent automatically spawns `npx -y slack-mcp-server@latest --transport stdio`
- Server runs as subprocess, terminated when agent stops
- No manual server management needed

## Option 2: SSE Transport (Server-Sent Events)

Connect to a separately running Slack MCP server via HTTP.

**Start the server** (in a separate terminal):
```bash
# Using npx
npx -y slack-mcp-server@latest --transport sse

# Or using Docker
docker run -d -p 13080:13080 \
  -e SLACK_MCP_XOXP_TOKEN=xoxp-... \
  ghcr.io/korotovsky/slack-mcp-server \
  mcp-server --transport sse
```

**Configuration** (`.env`):
```env
SLACK_MCP_TRANSPORT=sse
SLACK_MCP_SERVER_URL=http://127.0.0.1:13080/sse
SLACK_MCP_API_KEY=your-api-key-here  # Optional, for authentication
# Authentication tokens
SLACK_MCP_XOXP_TOKEN=xoxp-your-token-here
```

**When to use**:
- Multiple clients connecting to same server
- Remote server deployment
- Better debugging (server logs separate from agent)

## Option 3: Docker Compose Deployment

For production or team usage:

```bash
cd community_chatbot/mcp/slack
wget -O docker-compose.yml https://github.com/korotovsky/slack-mcp-server/releases/latest/download/docker-compose.yml
wget -O .env https://github.com/korotovsky/slack-mcp-server/releases/latest/download/default.env.dist

# Edit .env with your tokens
nano .env

# Start services
docker network create app-tier
docker-compose up -d
```