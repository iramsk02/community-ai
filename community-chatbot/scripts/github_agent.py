from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
import re
import asyncio
from contextlib import asynccontextmanager

load_dotenv()

# os.environ['GITHUB_APP_PRIVATE_KEY'] = """ Replace with the actual private key """

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Global variables
agent_executor = None
chat_sessions = {}

def sanitize_tool_name(name: str) -> str:
    """Convert tool name to a valid function name."""
    name = name.lower().replace("'", "").replace("'", "")
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name) 
    return name.strip("_")

def initialize_agent():
    """Initialize the GitHub agent with tools."""
    global agent_executor
    
    # Verify required environment variables are loaded
    required_vars = [
        "OPENAI_API_KEY",
        "GITHUB_APP_ID", 
        "GITHUB_REPOSITORY",
        "GITHUB_BRANCH",
        "GITHUB_BASE_BRANCH",
        "GITHUB_APP_PRIVATE_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Initialize GitHub wrapper and toolkit
    github = GitHubAPIWrapper()
    toolkit = GitHubToolkit.from_github_api_wrapper(github)
    
    # Get and sanitize tools
    tools = toolkit.get_tools()
    for tool in tools:
        tool.name = sanitize_tool_name(tool.name)
    
    # Initialize LLM and create agent
    llm = init_chat_model("gpt-4o-mini", model_provider="openai")
    agent_executor = create_react_agent(llm, tools)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        initialize_agent()
        print("GitHub Agent initialized successfully")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        raise
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="GitHub Agent API",
    description="A FastAPI backend for GitHub LangGraph agent",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "GitHub Agent API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatMessage):
    """Chat with the GitHub agent."""
    global agent_executor, chat_sessions
    
    if agent_executor is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    session_id = request.session_id
    user_message = request.message
    
    # Initialize session if it doesn't exist
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # Add user message to chat history
    chat_sessions[session_id].append(("user", user_message))
    
    try:
        # Stream events from the agent
        events = agent_executor.stream(
            {"messages": chat_sessions[session_id]},
            stream_mode="values"
        )
        
        # Get the last message from the agent
        last_msg = None
        for event in events:
            last_msg = event["messages"][-1]
        
        if last_msg:
            response_content = last_msg.content
            # Add assistant response to chat history
            chat_sessions[session_id].append(("assistant", response_content))
        else:
            response_content = "Sorry, I couldn't process your request."
        
        return ChatResponse(response=response_content, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/sessions")
async def get_sessions():
    """Get all active chat sessions."""
    return {"sessions": list(chat_sessions.keys())}

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific chat session."""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent_initialized": agent_executor is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
