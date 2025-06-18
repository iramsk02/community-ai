# main.py
import os
import json
from data import main as extract_slack_messages
from dotenv import load_dotenv
from vectordb import create_vector_database, query_vector_database, generate_llm_response

# Load environment variables
load_dotenv()

def run_pipeline(channel_ids=None, days_back=30, output_file="slack_raw_data.json"):
    """
    Run the data extraction pipeline from Slack.
    
    Args:
        channel_ids (list, optional): Specific channel IDs to extract from
        days_back (int, optional): How many days back to extract messages
        output_file (str): Filename to save the extracted data
    """
    print("Starting Slack message extraction...")
    documents = extract_slack_messages(
        channel_ids=channel_ids,
        days_back=days_back,
        output_file=output_file
    )
    
    print(f"Extracted {len(documents)} channels.")
    print(f"Raw data saved to {output_file}")
    
    # Save the processed messages as plain text
    with open("processed_messages.txt", "w", encoding="utf-8") as f:
        for channel_id, channel_data in documents.items():
            channel_name = channel_data.get("name", channel_id)
            for msg in channel_data.get("messages", []):
                user = msg.get("user", "unknown")
                date = msg.get("ts", "unknown")
                content = msg.get("text", "")
                f.write(f"Channel: #{channel_name}\nUser: {user}\nDate: {date}\nContent: {content}\n\n")
    
    print(f"Processed messages saved to processed_messages.txt")
    return documents

def display_sample_messages(documents, count=5):
    """Display a sample of the extracted messages."""
    # Flatten all messages from all channels
    all_messages = []
    for channel_id, channel_data in documents.items():
        channel_name = channel_data.get("name", channel_id)
        for msg in channel_data.get("messages", []):
            all_messages.append({
                "channel_name": channel_name,
                "user": msg.get("user", "unknown"),
                "date": msg.get("ts", "unknown"),
                "content": msg.get("text", "")
            })

    sample_count = min(count, len(all_messages))
    print(f"\nShowing {sample_count} sample messages:")


def prepare_documents_for_vectordb(slack_data):
    """
    Convert slack data to the format needed for the vector database.
    
    Args:
        slack_data (dict): Dictionary containing slack channel data
    
    Returns:
        list: Documents formatted for vector database
    """
    documents = []
    
    for channel_id, channel_data in slack_data.items():
        channel_name = channel_data.get("name", channel_id)
        
        for msg in channel_data.get("messages", []):
            user = msg.get("user", "unknown")
            date = msg.get("ts", "unknown")
            content = msg.get("text", "")
            
            if content:  # Only add non-empty messages
                documents.append({
                    "content": content,
                    "metadata": {
                        "channel": channel_name,
                        "user": user,
                        "timestamp": date
                    }
                })
    
    return documents

def run_chat_cli(persist_directory="./slack_vectordb"):
    """
    Run a command-line interface to interact with the LLM using the vector database.
    
    Args:
        persist_directory (str): Path to the vector database
    """
    print("\n" + "="*50)
    print("Welcome to the Mifos Community Chat Assistant!")
    print("Ask any question about Mifos or related to the Slack messages.")
    print("Type 'exit' to quit.")
    print("="*50 + "\n")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the Mifos Chat Assistant. Goodbye!")
            break
        
        print("\nAssistant: ", end="")
        
        try:
            response = generate_llm_response(user_input, persist_directory=persist_directory)
            print(response)
        except Exception as e:
            print(f"Sorry, I encountered an error: {str(e)}")

if __name__ == "__main__":
    # Check if vector database already exists
    persist_directory = "./slack_vectordb"
    
    if not os.path.exists(persist_directory):
        print("Vector database not found. Creating new database...")
        
        # Extract data from Slack
        slack_data = run_pipeline(
            channel_ids=["C5KKAMQCW"], 
            days_back=100
        )
        
        # Display sample of extracted messages
        display_sample_messages(slack_data)
        
        # Prepare documents for vector database
        documents = prepare_documents_for_vectordb(slack_data)
        
        # Create the vector database
        print(f"\nCreating vector database with {len(documents)} documents...")
        create_vector_database(documents, persist_directory=persist_directory)
        print("Vector database created successfully!")
    else:
        print(f"Using existing vector database at {persist_directory}")
    
    # Start the CLI chat interface
    run_chat_cli(persist_directory=persist_directory)