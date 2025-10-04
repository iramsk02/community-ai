from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
import os
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Pydantic models--
class JiraQueryRequest(BaseModel):
    query: str
    use_fallback: bool = True 

class JiraQueryResponse(BaseModel):
    response: str
    query_used: str
    method_used: str 
    success: bool

# Create the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize components on startup
    initialize_jira_components()
    yield
    # Clean up on shutdown (if needed)

# Define app with lifespan
app = FastAPI(title="Jira Agent API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware IMMEDIATELY after app definition
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
jira_agent = None
jira_wrapper = None
llm = None
jql_generation_prompt = None
summarization_prompt = None

def initialize_jira_components():
    """Initialize all Jira and LangChain components"""
    global jira_agent, jira_wrapper, llm, jql_generation_prompt, summarization_prompt
    
    print("Initializing Jira and LangChain components...")
    
    # Initialize Jira components
    jira_wrapper = JiraAPIWrapper()
    toolkit = JiraToolkit.from_jira_api_wrapper(jira_wrapper)
    tools = toolkit.get_tools()
    
    # Initialize LLM
    llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")
    
    # Agent configuration
    agent_kwargs = {
        "prefix": """You are a specialized Jira assistant.
You MUST use the provided tools to answer questions about Jira.
Do NOT answer any questions from your own knowledge.
If a user's query seems like a general knowledge question, you MUST assume it refers to data within Jira.

*** CRITICAL JQL RULE ***
When filtering by a field with a string value that contains spaces (like a person's name, a project name, or a summary), you MUST enclose the value in single or double quotes.
CORRECT: assignee = 'Aru Sharma'
INCORRECT: assignee = Aru Sharma
CORRECT: summary ~ '"New Login Button"'
INCORRECT: summary ~ 'New Login Button'

Always format your response as a Thought, an Action, and an Action Input.
Begin!"""
    }
    
    # Initialize agent
    jira_agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs=agent_kwargs,
    )
    
    # Initialize prompts
    jql_generation_prompt = PromptTemplate.from_template(
        """You are an expert in Jira Query Language (JQL). Your sole task is to convert a user's natural language request into a valid JQL query.
You must only respond with the JQL query string and nothing else.

--- Important JQL Syntax Rules ---
1.  **Quoting:** Any string value containing spaces or special characters MUST be enclosed in single ('') or double ("") quotes.
    -   Example for a name: `assignee = 'Aru Sharma'`
    -   Example for a search phrase: `summary ~ '"Detailed new feature"'`
2.  **Usernames:** When searching for an assignee, it is best to use their name in quotes.

--- Examples ---
User Request: "find all tickets in the 'PROJ' project"
JQL Query: project = 'PROJ'

User Request: "show me all open bugs in the 'Mobile' project assigned to Aru Sharma"
JQL Query: project = 'Mobile' AND issuetype = 'Bug' AND status = 'Open' AND assignee = 'Aru Sharma'

User Request: "what were the top 5 highest priority issues created last week?"
JQL Query: created >= -7d ORDER BY priority DESC

Now, convert the following user request into a JQL query.

User Request: "{user_query}"
JQL Query:"""
    )
    
    summarization_prompt = PromptTemplate.from_template(
        """You are a helpful assistant. The user asked the following question:

"{user_query}"

An AI agent attempted to answer this but failed. As a fallback, we ran a JQL query and got the following raw Jira issue data.
Please analyze this data and provide a clear, concise, and helpful answer to the user's original question. If the data seems irrelevant or empty, state that you couldn't find relevant information.

JSON Data:
{json_data}

Based on the data, answer the user's question.
"""
    )

def intelligent_agent_run(query: str):
    """
    Tries to run the main agent. If it fails, it uses an LLM to generate
    a JQL query from the user's input and executes that instead.
    """
    try:
        print("--- Attempting main agent execution ---")
        response = jira_agent.run(query)
        return {
            "response": response,
            "method_used": "agent",
            "query_used": query,
            "success": True
        }
    except Exception as e:
        print("\n--- Agent failed, switching to intelligent fallback mode ---")
        print(f"Error: {e}\n")

        # Use the LLM to generate a JQL query from the user's original query
        print("Generating JQL from natural language...")
        jql_generation_chain = jql_generation_prompt | llm
        generated_jql = jql_generation_chain.invoke({"user_query": query}).content
        generated_jql = generated_jql.strip().strip("'\"")
        print(f"Dynamically Generated JQL: '{generated_jql}'")

        # Execute the generated JQL query
        print("Executing generated JQL query...")
        try:
            fallback_data = jira_wrapper.run(mode="jql", query=generated_jql)

            if not fallback_data:
                return {
                    "response": "The generated JQL query ran successfully but returned no issues. Please try rephrasing your request or be more specific.",
                    "method_used": "fallback",
                    "query_used": generated_jql,
                    "success": True
                }

            # Use the LLM to summarize the results for the user
            print("Summarizing JQL results for the user...")
            summarization_chain = summarization_prompt | llm
            
            final_response = summarization_chain.invoke({
                "user_query": query,
                "json_data": fallback_data 
            }).content
            
            return {
                "response": final_response,
                "method_used": "fallback",
                "query_used": generated_jql,
                "success": True
            }

        except Exception as fallback_e:
            print(f"Fallback JQL execution also failed: {fallback_e}")
            return {
                "response": f"I'm sorry, I couldn't process your request. Both the primary agent and the fallback query failed. The last error was: {fallback_e}",
                "method_used": "failed",
                "query_used": query,
                "success": False
            }
@app.options("/jira/query")
async def options_jira_query():
    return {}

@app.post("/jira/query", response_model=JiraQueryResponse)
async def query_jira(request: JiraQueryRequest):
    """Main endpoint to query Jira using natural language"""
    try:
        if not jira_agent:
            raise HTTPException(status_code=500, detail="Jira agent not initialized")
        
        if request.use_fallback:
            result = intelligent_agent_run(request.query)
        else:
            # Use only the main agent without fallback
            try:
                response = jira_agent.run(request.query)
                result = {
                    "response": response,
                    "method_used": "agent",
                    "query_used": request.query,
                    "success": True
                }
            except Exception as e:
                result = {
                    "response": f"Agent failed: {str(e)}",
                    "method_used": "agent",
                    "query_used": request.query,
                    "success": False
                }
        
        return JiraQueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jira/direct-jql")
async def direct_jql_query(jql_query: str):
    """Direct JQL query endpoint"""
    try:
        if not jira_wrapper:
            raise HTTPException(status_code=500, detail="Jira wrapper not initialized")
        
        result = jira_wrapper.run(mode="jql", query=jql_query)
        return {
            "jql_query": jql_query,
            "result": result,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jira/generate-jql")
async def generate_jql(natural_query: str):
    """Generate JQL from natural language"""
    try:
        if not llm or not jql_generation_prompt:
            raise HTTPException(status_code=500, detail="Components not initialized")
        
        jql_generation_chain = jql_generation_prompt | llm
        generated_jql = jql_generation_chain.invoke({"user_query": natural_query}).content
        generated_jql = generated_jql.strip().strip("'\"")
        
        return {
            "natural_query": natural_query,
            "generated_jql": generated_jql,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "jira_initialized": jira_agent is not None,
        "wrapper_initialized": jira_wrapper is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
