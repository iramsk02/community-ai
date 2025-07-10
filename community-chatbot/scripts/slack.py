from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from dotenv import load_dotenv
from langchain_community.agent_toolkits import SlackToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import os
from fastapi.middleware.cors import CORSMiddleware  # Add this import

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str  # "user" or "agent"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"  # To maintain separate conversations

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

# FastAPI app
app = FastAPI(title="Slack Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store agents and conversations
agents: Dict[str, Any] = {}
conversations: Dict[str, List] = {}

# Initialize the agent
def initialize_agent():
    llm = ChatOpenAI(model="gpt-4o-mini")
    toolkit = SlackToolkit()
    tools = toolkit.get_tools()
    return create_react_agent(llm, tools)

@app.on_event("startup")
async def startup_event():
    """Initialize the agent when the server starts"""
    global agents
    agents["default"] = initialize_agent()
    # Initialize the default conversation
    conversations["1"] = []  # Add this line to create the default conversation

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Get or create conversation
        if request.conversation_id not in conversations:
            conversations[request.conversation_id] = []
        
        # Get the agent (create if doesn't exist)
        if request.conversation_id not in agents:
            agents[request.conversation_id] = initialize_agent()
        
        agent = agents[request.conversation_id]
        conversation = conversations[request.conversation_id]
        
        # Add user message to conversation
        conversation.append(("user", request.message))
        
        # Get agent response
        events = agent.stream({"messages": conversation}, stream_mode="values")
        
        # Process the stream to get the final response
        final_response = ""
        final_event = None
        
        for event in events:
            final_event = event
            message = event["messages"][-1]
            if hasattr(message, 'content') and message.type == "ai":
                # Check if it's not a tool call
                if not (hasattr(message, 'tool_calls') and message.tool_calls):
                    final_response = message.content
        
        # Update conversation with the final state
        if final_event:
            conversations[request.conversation_id] = final_event["messages"]
        
        # If no response found, provide a default
        if not final_response:
            final_response = "I processed your request, but didn't generate a text response."

        if not isinstance(final_response, str):
            final_response = str(final_response)
        
        return ChatResponse(
            response=final_response,
            conversation_id=request.conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in conversations:
        # Instead of 404, create an empty conversation
        conversations[conversation_id] = []
    
    # Convert conversation to readable format
    formatted_conversation = []
    
    for message in conversations[conversation_id]:
        # Handle different message types
        if hasattr(message, 'type') and hasattr(message, 'content'):
            # LangChain message object
            formatted_conversation.append({
                "role": message.type,
                "content": str(message.content)
            })
        elif isinstance(message, tuple) and len(message) == 2:
            # Tuple format (role, content)
            role, content = message
            formatted_conversation.append({
                "role": role,
                "content": str(content)
            })
        else:
            # Fallback for other formats
            formatted_conversation.append({
                "role": "unknown",
                "content": str(message)
            })
    
    return {"conversation_id": conversation_id, "messages": formatted_conversation}

@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear a specific conversation"""
    if conversation_id in conversations:
        conversations[conversation_id] = []
    if conversation_id in agents and conversation_id != "default":
        del agents[conversation_id]
    
    return {"message": f"Conversation {conversation_id} cleared"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)