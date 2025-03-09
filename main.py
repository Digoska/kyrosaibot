import os
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Flask app for Railway pinging
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Support Bot is Running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# Telegram Bot Code
# Define conversation states
ISSUE_TYPE, ISSUE_DETAILS = range(2)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to Support Bot!\nPlease tell us what type of issue you're facing (e.g., Technical, Billing, etc.)."
    )
    return ISSUE_TYPE

def issue_type(update: Update, context: CallbackContext):
    context.user_data['issue_type'] = update.message.text
    update.message.reply_text("Thanks. Now, please provide more details about your issue.")
    return ISSUE_DETAILS

def issue_details(update: Update, context: CallbackContext):
    context.user_data['issue_details'] = update.message.text

    # Get the admin chat id from an environment variable
    admin_chat_id = int(os.environ.get("7295071438", "0"))
    summary = (
        f"New support request:\n"
        f"Issue Type: {context.user_data['issue_type']}\n"
        f"Details: {context.user_data['issue_details']}\n"
        f"From: {update.message.from_user.username or update.message.from_user.id}"
    )
    context.bot.send_message(chat_id=admin_chat_id, text=summary)
    update.message.reply_text("Your request has been received. Our team will get back to you shortly.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def run_bot():
    # Get your bot token from an environment variable
    token = os.environ.get("7284527981:AAEN9XKdRh-r9LYgLUCEYFrrcyRdbihyhWs")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ISSUE_TYPE: [MessageHandler(Filters.text & ~Filters.command, issue_type)],
            ISSUE_DETAILS: [MessageHandler(Filters.text & ~Filters.command, issue_details)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Start Flask web server in a separate thread for Railway
    threading.Thread(target=run_web).start()
    # Start the Telegram bot
    run_bot()
