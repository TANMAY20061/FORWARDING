import logging
import random
import time
import asyncio
from flask import Flask
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from multiprocessing import Process

# Flask App Initialization
app = Flask(__name__)

@app.route('/')
def index():
    return "Flask server is running successfully!"

# Function to Start the Flask App
def start_flask():
    app.run(host="0.0.0.0", port=10000, threaded=True)

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Replace with your Bot Token and Channel ID
BOT_TOKEN = "7202087814:AAHUpeC_uXQ54VwJkZtwMzGa4juGEGAJmkg"
CHANNEL_ID = "-1002313229856"
ADMIN_USER_ID = 5181364124  # Replace with your admin's Telegram user ID
GROUP_LINK = "https://t.me/your_group_link"  # Replace with your group's link

bot = Bot(token=BOT_TOKEN)
posting_active = False  # Flag to track if predictions are being posted

# Generate the period code based on current time
def generate_period_code():
    """Generate a period number based on current time."""
    calendar = time.gmtime()
    total_minutes = calendar.tm_hour * 60 + calendar.tm_min
    period_code = f"{time.strftime('%Y%m%d', calendar)}1000{10001 + total_minutes}"
    return period_code

# Fetch the result from the API for a given period
def fetch_result_from_api(period_code):
    """Fetch the actual result for the given period from the API."""
    try:
        # Simulating an API fetch based on period code
        result_from_api = random.choice(["BIG", "SMALL"])
        return result_from_api
    except Exception as e:
        logging.error(f"Error fetching result from API: {e}")
    return None

# Send prediction message to channel
async def send_prediction():
    """Send prediction to the channel and maintain status."""
    global posting_active
    while True:
        if posting_active:
            try:
                period_code = generate_period_code()
                last_5_digits = period_code[-5:]  # Extract last 5 digits

                prediction = random.choice(["BIG", "SMALL"])

                message = (
                    f"❤️🔥 <b>Prediction:</b>\n\n"
                    f"🕹 <b>Game:</b> Wingo 1 Min\n\n"
                    f"📟 <b>Period Number:</b> {period_code}\n\n"
                    f"🎰 <b>Prediction:</b> 🍤 {prediction} 🍤\n\n"
                    f"Last 5 Digits: <b>{last_5_digits}</b>\n\n"
                    f"<b>STATUS:</b> WAITING FOR RESULT\n\n"
                    f"✅ Make your own bot DM: @TANMAYPAUL21"
                )

                sent_message = await bot.send_message(
                    chat_id=CHANNEL_ID, text=message, parse_mode="HTML"
                )

                await asyncio.sleep(30)  # Wait for some time before updating status

                result_from_api = fetch_result_from_api(period_code)

                if result_from_api is None:
                    final_status = "RESULT NOT FOUND"
                else:
                    final_status = "WIN" if prediction == result_from_api else "LOSS"

                updated_message = (
                    f"❤️🔥 <b>Prediction:</b>\n\n"
                    f"🕹 <b>Game:</b> Wingo 1 Min\n\n"
                    f"📟 <b>Period Number:</b> {period_code}\n\n"
                    f"🎰 <b>Prediction:</b> 🍤 {prediction} 🍤\n\n"
                    f"Last 5 Digits: <b>{last_5_digits}</b>\n\n"
                    f"<b>STATUS:</b> {final_status}\n\n"
                    f"✅ Make your own bot DM: @TANMAYPAUL21"
                )

                await bot.edit_message_text(
                    chat_id=CHANNEL_ID,
                    message_id=sent_message.message_id,
                    text=updated_message,
                    parse_mode="HTML",
                )

                await asyncio.sleep(60 - time.gmtime().tm_sec)

            except Exception as e:
                logging.error(f"Error sending prediction: {e}")
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)

# /post command to start posting predictions (admin only)
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start posting predictions in the group."""
    if update.effective_user.id == ADMIN_USER_ID:
        global posting_active
        posting_active = True
        await update.message.reply_text("Bot will now start posting predictions every minute.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

# /stop command to stop posting predictions (admin only)
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop posting predictions in the group."""
    if update.effective_user.id == ADMIN_USER_ID:
        global posting_active
        posting_active = False
        await update.message.reply_text("Bot has stopped posting predictions.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

# /prediction command for users to see the next prediction in bot
async def prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the next prediction in the bot."""
    period_code = generate_period_code()
    last_5_digits = period_code[-5:]
    prediction = random.choice(["BIG", "SMALL"])

    message = (
        f"❤️🔥 <b>Prediction:</b>\n\n"
        f"🕹 <b>Game:</b> Wingo 1 Min\n\n"
        f"📟 <b>Period Number:</b> {period_code}\n\n"
        f"🎰 <b>Prediction:</b> 🍤 {prediction} 🍤\n\n"
        f"Last 5 Digits: <b>{last_5_digits}</b>\n\n"
        f"✅ Make your own bot DM: @TANMAYPAUL21"
    )

    await update.message.reply_text(message, parse_mode="HTML")

# /start command for new users
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text(
            f"The BOT IS ONLY AVAILABLE IN THIS GROUP: {GROUP_LINK}"
        )
    else:
        await update.message.reply_text(
            "Welcome to the Prediction Bot!\n\n"
            "Commands:\n"
            "/prediction - See the prediction for the current period.\n"
            "/post - Start posting predictions in the group (admin only).\n"
            "/stop - Stop posting predictions (admin only)."
        )

def run_bot():
    """Run the bot in an already running loop (for Pydroid 3)."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prediction", prediction))
    application.add_handler(CommandHandler("post", post))
    application.add_handler(CommandHandler("stop", stop))

    # Run the background task in an asyncio loop
    loop = asyncio.get_event_loop()
    loop.create_task(send_prediction())  # Start sending predictions in the background

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    flask_process = Process(target=start_flask)
    flask_process.start()
    run_bot()
