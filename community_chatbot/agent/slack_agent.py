import os
import argparse
from dotenv import load_dotenv

load_dotenv()

from langchain_community.agent_toolkits import SlackToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o-mini")

toolkit = SlackToolkit()
tools = toolkit.get_tools()

agent_executor = create_react_agent(llm, tools)

def chat_with_agent():
    print("Agent is ready! Type your message or 'exit' to quit.\n")
    
    conversation = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting chat. Goodbye!")
            break

        conversation.append(("user", user_input))

        events = agent_executor.stream({"messages": conversation}, stream_mode="values")
        for event in events:
            message = event["messages"][-1]
            if message.type != "tool":
                print("Agent:", end=" ", flush=True)
                message.pretty_print()
        
        conversation = event["messages"]

if __name__ == "__main__":
    chat_with_agent()