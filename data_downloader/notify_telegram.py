import json
from telegram.ext import Updater


def notify_error(message: str):
    with open('data_downloader/telegram_data.json') as data:
        telegram_data = data.read()
    telegram_data = json.loads(telegram_data)


    bot_token = telegram_data["token"]
    chat_id = telegram_data["chat-id"]

    # Create the Telegram bot
    updater = Updater(bot_token)

    # Send the message to the Telegram bot
    try:
        updater.bot.send_message(chat_id, message)
        print("> error message sent to telegram")
    except:
        # take only the last 4000 characters of the message
        updater.bot.send_message(chat_id, message[-4000:])
        print("> error message sent to telegram")
