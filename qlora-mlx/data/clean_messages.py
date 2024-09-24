import json
import re
import random
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
my_username = "wilbur" 

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

    # Assign roles based on the 'from' field and format as required
    if message['from'] == my_username:  # Check if the message is from "Wilbur"
        # Find the user message that preceded this one
        previous_message = formatted_messages[-1] if formatted_messages else None
        if previous_message and previous_message.get('role') == 'user':
            # Format the message according to the required structure
            formatted_messages.append({
                "text": f"<s>[INST] WilburBOT, functioning as a Telegram bot that is supposed to mimic the speech of its creator, Wilbur, and ends responses with its signature '–WilburBOT'. "
                        "WilburBOT will tailor the length of its responses to match the user's message, providing concise responses to any kind of messages or sentiments, whether it is toward "
                        "the bot itself or someone else, thus keeping the interaction natural and engaging.\n\nPlease respond to the following comment.\n\n"
                        f"{{ {previous_message['content']} }}\n[/INST]\n{{ {text_content} –WilburBOT }}</s>"
            })
    else:  # If not from "Wilbur", it is considered a "user" message
        formatted_messages.append({
            "role": "user",
            "content": text_content
        })

# Shuffle the formatted messages for random partitioning
random.shuffle(formatted_messages)

# Calculate the sizes for train, test, and validation sets
total_messages = len(formatted_messages)
train_size = int(0.7 * total_messages)
valid_size = int(0.15 * total_messages)
test_size = total_messages - train_size - valid_size

# Partition the data
train_data = formatted_messages[:train_size]
valid_data = formatted_messages[train_size:train_size + valid_size]
test_data = formatted_messages[train_size + valid_size:]

# Function to save messages to a .jsonl file
def save_jsonl(filename, data):
    with open(filename, "w", encoding='utf-8') as f:
        for message in data:
            json.dump(message, f, ensure_ascii=False)
            f.write("\n")

# Save the partitioned data to separate files
save_jsonl("train.jsonl", train_data)
save_jsonl("valid.jsonl", valid_data)
save_jsonl("test.jsonl", test_data)

# Save the formatted messages in JSONL format
# with open("cleaned_data.jsonl", "w", encoding='utf-8') as f:
#     for message in formatted_messages:
#         json.dump(message, f, ensure_ascii=False)
#         f.write("\n")

# Define the start pattern you want to keep
start_pattern = '{"text": "<s>[INST] WilburBOT, functioning as a Telegram'

# Function to filter a .jsonl file
def filter_jsonl(file_path, output_file_path):
    with open(file_path, 'r', encoding='utf-8') as infile, open(output_file_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.startswith(start_pattern):
                outfile.write(line)
                
filter_jsonl("train.jsonl", "train_filtered.jsonl")
filter_jsonl("valid.jsonl", "valid_filtered.jsonl")
filter_jsonl("test.jsonl", "test_filtered.jsonl")

print("Filtering complete. New filtered files have been created.")
