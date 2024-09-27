import json
import re
import random

url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

def load_keywords(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

files = ["chatdata1.json", "chatdata2.json"]

def load_json_files(files):
    messages = []
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            messages += data['messages']
    return messages

def contains_keywords(message, keywords):
    return any(keyword.lower() in message.lower() for keyword in keywords)

def remove_urls(message):
    return re.sub(url_pattern, '', message)

def combine_consecutive_messages(messages):
    combined_messages = []
    previous_message = None
    
    for message in messages:
        if 'from' not in message:
            continue
        
        if isinstance(message['text'], str):
            text_content = message['text']
        else:
            text_content = " ".join([item['text'] if isinstance(item, dict) else item for item in message['text']])
        
        text_content = remove_urls(text_content).strip()
        
        if previous_message and message['from'] == previous_message['from']:
            previous_message['text'] += " " + text_content
        else:
            if previous_message:
                combined_messages.append(previous_message)
            previous_message = message
            previous_message['text'] = text_content
    
    if previous_message:
        combined_messages.append(previous_message)
    
    return combined_messages

keywords = load_keywords("keywords_to_filter.txt")
data = load_json_files(files)
combined_data = combine_consecutive_messages(data)
formatted_messages = []
my_username = "wilbur"
# Loop through each message and format with the prompt, skipping messages with keywords and removing URLs
for i, message in enumerate(combined_data):
    # Skip if there's no "from" field in the message
    if 'from' not in message:
        continue
    if contains_keywords(message['text'], keywords):
        continue

    # Assign roles based on the 'from' field and format as required
    if message['from'] == my_username:  # Check if the message is from "me"
        #seeing if the previous message is from the same user
        previous_message = formatted_messages[-1] if formatted_messages else None
        if previous_message and previous_message.get('role') == 'user':
            formatted_messages.append({
                "text": f"<s>[INST] WilburBOT, functioning as a Telegram bot that is supposed to mimic the speech of its creator, Wilbur, and ends responses with its signature '–WilburBOT'. "
                        "WilburBOT will answer in a verbose manner if it wishes, comedic responses to any kind of messages or sentiments, whether it is toward "
                        "the bot itself or someone else, thus keeping the interaction natural and engaging.\n\nPlease respond to the following comment.\n\n"
                        f"{{ {previous_message['content']} }}\n[/INST]\n{{ {message['text']} –WilburBOT }}</s>"
            })
    else:  # if it's not from me, then it must be from someone else, we'll call all of them "user"
        formatted_messages.append({
            "role": "user",
            "content": message['text']
        })

def filter_out_user_only_messages(formatted_messages):
    return [msg for msg in formatted_messages if msg.get('text') and msg['text'].startswith('<s>[INST]')]

formatted_messages = filter_out_user_only_messages(formatted_messages)
random.shuffle(formatted_messages)

total_messages = len(formatted_messages)
train_size = int(0.7 * total_messages)
valid_size = int(0.15 * total_messages)
test_size = total_messages - train_size - valid_size

# Partition the data into training data, valid data, and test data.
train_data = formatted_messages[:train_size]
valid_data = formatted_messages[train_size:train_size + valid_size]
test_data = formatted_messages[train_size + valid_size:]

# Function to save messages to a .jsonl file
def save_jsonl(filename, data):
    with open(filename, "w", encoding='utf-8') as f:
        for message in data:
            json.dump(message, f, ensure_ascii=False)
            f.write("\n")

save_jsonl("train.jsonl", train_data)
save_jsonl("valid.jsonl", valid_data)
save_jsonl("test.jsonl", test_data)