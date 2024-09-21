import json
import re

# Regular expression pattern to match URLs
url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

# Load the keywords from a separate file
def load_keywords(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

# Load the JSON data
files = ["chatdata1.json", "chatdata2.json"]

# Load multiple JSON files into a single list of messages
def load_json_files(files):
    messages = []
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            # Extract the messages from the nested structure
            messages += data['messages']
    return messages

# Function to check if a message contains any keywords
def contains_keywords(message, keywords):
    return any(keyword.lower() in message.lower() for keyword in keywords)

# Function to remove URLs from a message
def remove_urls(message):
    return re.sub(url_pattern, '', message)

# Load the keywords from the external file
keywords = load_keywords("keywords_to_filter.txt")

# Load the messages from the files
data = load_json_files(files)

# Initialize the list to store formatted messages
formatted_messages = []

# Define the username for filtering
my_username = "wilbur"  # Make sure this matches exactly as it appears in the "from" field

# Loop through each message and format accordingly, skipping messages with keywords and removing URLs
for message in data:
    # Skip if there's no 'from' field in the message
    if 'from' not in message:
        continue
    
    # Extract the text from the message
    if isinstance(message['text'], str):
        text_content = message['text']
    else:
        text_content = " ".join([item['text'] if isinstance(item, dict) else item for item in message['text']])
    
    # Remove URLs from the text
    text_content = remove_urls(text_content).strip()
    
    # Skip the message if it contains any of the keywords
    if contains_keywords(text_content, keywords):
        continue

    # Assign roles based on the 'from' field
    if message['from'] == my_username:  # Check if the message is from "Wilbur"
        formatted_messages.append({
            "role": "assistant",
            "content": text_content
        })
    else:  # If not from "Wilbur", it is considered a "user" message
        formatted_messages.append({
            "role": "user",
            "content": text_content
        })

# Save the formatted messages in JSONL format
with open("cleaned_data.jsonl", "w", encoding='utf-8') as f:
    for message in formatted_messages:
        json.dump(message, f, ensure_ascii=False)
        f.write("\n")