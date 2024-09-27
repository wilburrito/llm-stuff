import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import os
import subprocess
from dotenv import load_dotenv
import signal

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Async command to start the bot
async def start(update: Update, context):
    logger.info("Received start command")
    await update.message.reply_text('NOOBS')

async def handle_message(update: Update, context):
    logger.info(f"Received message: {update.message.text}")
    user_message = update.message.text
    response = generate_response(user_message)
    logger.info("Sending response: %s", response)
    await update.message.reply_text(response)

def clean_response(response):
    """
    Extracts the response after the [/INST] token and removes curly braces.
    """
    if "[/INST]" in response:
        # Split the response at [/INST] and get the part after it
        response = response.split("[/INST]")[1].strip()
        response = response.split("=")[0].strip()

    # Remove the curly braces if they are around the response
    response = response.replace("{", "").replace("}", "").strip()

    return response

# Adjusted generate_response function to run lora.py script via subprocess
def generate_response(user_input):
    model_path = "mlx-community/Mistral-7B-Instruct-v0.2-4bit"
    adapter_path = "qlora-mlx/adapters_v2.npz"

    instruction = "<s>[INST] WilburBOT, functioning as a Telegram bot that is supposed to mimic the speech of its creator, Wilbur, and ends responses with its signature '–WilburBOT'. WilburBOT will tailor its responses to reply to the user's message, providing verbose responses to any kind of messages or sentiments, whether it is toward the bot itself or someone else, thus keeping the interaction natural and engaging.\n\nPlease respond to the following comment.\n\n{ " + user_input + " }\n[/INST]"
    
    # Define the command to run lora.py with the user's input
    command = ['python', 'qlora-mlx/scripts/lora.py', '--model', model_path, '--adapter-file', adapter_path, '--max-tokens', '150', '--prompt', instruction]
    
    try:
        # Run the command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        logger.info(f"Subprocess output: {result.stdout}")
        logger.error(f"Subprocess error: {result.stderr}")

        # Check for errors
        if result.returncode != 0:
            logger.error(f"Error during generation: {result.stderr}")
            return "Sorry, I couldn't process that message."
        
        # Return the model's generated response
        cleaned_response = clean_response(result.stdout.strip())
        return cleaned_response

    except Exception as e:
        logger.error(f"Error running subprocess: {e}")
        return "Sorry, an error occurred while processing your request."
    

def main():
    print("starting bot..")
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_API_TOKEN')
    
    application = ApplicationBuilder().token(telegram_token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    try:
        # Start polling and allow the bot to handle commands/messages
        print("Bot is polling...")
        application.run_polling(stop_signals=[signal.SIGINT, signal.SIGTERM])
    except (KeyboardInterrupt, SystemExit):
        print("Bot shutting down...")
        application.stop()  # Cleanly shut down the bot

if __name__ == '__main__':
    main()