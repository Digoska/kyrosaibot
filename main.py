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

# Define conversation states
ISSUE_TYPE, ISSUE_DETAILS = range(2)

def start(update: Update, context: CallbackContext):
    user = update.message.from_user.username or update.message.from_user.id
    print(f"[DEBUG] Received /start command from {user}")
    update.message.reply_text(
        "Welcome to Support Bot!\nPlease tell us what type of issue you're facing (e.g., Technical, Billing, etc.)."
    )
    return ISSUE_TYPE

def issue_type(update: Update, context: CallbackContext):
    user = update.message.from_user.username or update.message.from_user.id
    issue = update.message.text
    print(f"[DEBUG] Received issue type from {user}: {issue}")
    context.user_data['issue_type'] = issue
    update.message.reply_text("Thanks. Now, please provide more details about your issue.")
    return ISSUE_DETAILS

def issue_details(update: Update, context: CallbackContext):
    user = update.message.from_user.username or update.message.from_user.id
    details = update.message.text
    print(f"[DEBUG] Received issue details from {user}: {details}")
    context.user_data['issue_details'] = details

    # Get the admin chat ID from environment variables
    admin_chat_id_str = os.environ.get("ADMIN_CHAT_ID", "0")
    try:
        admin_chat_id = int(admin_chat_id_str)
    except Exception as e:
        print(f"[ERROR] Converting ADMIN_CHAT_ID to int failed: {e}")
        admin_chat_id = 0

    summary = (
        f"New support request:\n"
        f"Issue Type: {context.user_data['issue_type']}\n"
        f"Details: {context.user_data['issue_details']}\n"
        f"From: {user}"
    )
    print(f"[DEBUG] Forwarding summary to admin chat {admin_chat_id}: {summary}")
    try:
        context.bot.send_message(chat_id=admin_chat_id, text=summary)
    except Exception as e:
        print(f"[ERROR] Sending message to admin failed: {e}")
    update.message.reply_text("Your request has been received. Our team will get back to you shortly.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user.username or update.message.from_user.id
    print(f"[DEBUG] Operation cancelled by {user}")
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def run_bot():
    # Retrieve the bot token from environment variables
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("[ERROR] TELEGRAM_TOKEN is not set!")
        return
    print("[DEBUG] Starting bot with provided token.")
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
    print("[DEBUG] Bot polling started.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Start Flask web server in a separate thread for Railway
    threading.Thread(target=run_web).start()
    run_bot()
