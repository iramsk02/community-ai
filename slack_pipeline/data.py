import os
from datetime import datetime
import json
import time
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

def extract_channel_messages(channel_id, oldest=None, latest=None):
    """
    Extract all messages from a specific channel.
    
    Args:
        channel_id (str): The ID of the channel to extract messages from
        oldest (str, optional): Timestamp of the oldest message to fetch
        latest (str, optional): Timestamp of the latest message to fetch
        
    Returns:
        list: List of message objects
    """
    all_messages = []
    cursor = None
    
    while True:
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                result = client.conversations_history(
                    channel=channel_id,
                    cursor=cursor,
                    oldest=oldest,
                    latest=latest,
                    limit=1000 
                )
                
                messages = result["messages"]
                all_messages.extend(messages)
                
                # Check if there are more messages to fetch
                if result.get("has_more", False):
                    cursor = result["response_metadata"]["next_cursor"]
                    break
                else:
                    return all_messages
            
            except Exception as e:
                error_msg = str(e)
                if "not_in_channel" in error_msg:
                    print(f"ERROR: Bot is not in channel {channel_id}. Please add the bot to this channel in Slack using /invite @BotName")
                elif "rate_limited" in error_msg.lower():
                    wait_time = float(e.response.headers.get("Retry-After", 30))
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    attempts += 1
                else:
                    print(f"Error fetching messages: {e}")
                    return all_messages
        
        if attempts >= max_attempts:
            print("Max retry attempts reached for rate limiting")
            return all_messages
    
    return all_messages

def extract_all_channels_messages(channel_ids=None, oldest=None, latest=None):
    """
    Extract messages from all channels or a list of specific channels.
    
    Args:
        channel_ids (list, optional): List of channel IDs to extract from
        oldest (str, optional): Timestamp of the oldest message to fetch
        latest (str, optional): Timestamp of the latest message to fetch
        
    Returns:
        dict: Dictionary with channel IDs as keys and lists of messages as values
    """
    channels_data = {}
    
    # If no specific channels provided, get all visible channels
    if not channel_ids:
        try:
            result = client.conversations_list(types="public_channel,private_channel")
            channel_ids = [channel["id"] for channel in result["channels"]]
        except Exception as e:
            print(f"Error fetching channels: {e}")
            return channels_data
    
    # Extract messages from each channel
    for channel_id in channel_ids:
        try:
            # Get channel info
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
            print(f"Extracting messages from #{channel_name} ({channel_id})...")
            
            # Get messages
            messages = extract_channel_messages(channel_id, oldest, latest)
            channels_data[channel_id] = {
                "name": channel_name,
                "messages": messages
            }
            
            print(f"Extracted {len(messages)} messages from #{channel_name}")
            
        except Exception as e:
            print(f"Error processing channel {channel_id}: {e}")
    
    return channels_data

# Function to save extracted data to file
def save_data_to_file(data, filename=None):
    """Save the extracted data to a JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"slack_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return filename

## TODO: Add a function to process messages for vector database

def main(channel_ids=None, days_back=100, output_file=None):
    """
    Main function to extract messages and prepare them for vector database.
    
    Args:
        channel_ids (list, optional): Specific channel IDs to extract from
        days_back (int, optional): How many days back to extract messages
        output_file (str, optional): Filename to save raw data
    
    Returns:
        list: Processed documents ready for vector database
    """
    # Calculate timestamp for days_back
    if days_back:
        now = datetime.now().timestamp()
        oldest = str(now - (days_back * 24 * 60 * 60))
    else:
        oldest = None
    
    # Extract messages
    channels_data = extract_all_channels_messages(channel_ids, oldest)
    
    # Save raw data if needed
    if output_file:
        save_data_to_file(channels_data, output_file)
    
    return channels_data