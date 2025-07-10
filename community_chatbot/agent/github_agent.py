import os
import getpass
import re
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper

github = GitHubAPIWrapper()
toolkit = GitHubToolkit.from_github_api_wrapper(github)
tools = toolkit.get_tools()

def sanitize_tool_name(name: str) -> str:
    """Convert tool name to a valid function name: snake_case with only alphanumerics and _ or -."""
    name = name.lower().replace("'", "").replace("’", "")
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name) 
    return name.strip("_")

tools = toolkit.get_tools()

for tool in tools:
    tool.name = sanitize_tool_name(tool.name)

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

llm = init_chat_model("gpt-4o-mini", model_provider="openai")
tools = toolkit.get_tools()
agent_executor = create_react_agent(llm, tools)

print("GitHub Agent Chatbot (type 'exit' to quit)")
chat_history = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    chat_history.append(("user", user_input))

    try:
        events = agent_executor.stream(
            {"messages": chat_history},
            stream_mode="values"
        )

        for event in events:
            last_msg = event["messages"][-1]
            last_msg.pretty_print()

        chat_history.append(("assistant", last_msg.content))

    except Exception as e:
        print(f"[Error] {e}")
