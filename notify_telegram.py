import json
from telegram.ext import Updater


def notify_error(exception: Exception):
    with open('telegram_data.json') as data:
        telegram_data = data.read()
    telegram_data = json.loads(telegram_data)


    bot_token = telegram_data["token"]
    chat_id = telegram_data["chat-id"]

    # Compose the Telegram message
    message = f"Error in the Twitch Chat Listener \n Exception: {str(exception)}"

    # Create the Telegram bot
    updater = Updater(bot_token)

    # Send the message to the Telegram bot
    updater.bot.send_message(chat_id, message)
    print("error message sent to telegram")
