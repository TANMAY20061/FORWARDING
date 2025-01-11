import logging
import random
import time
import requests
import asyncio
from flask import Flask
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from multiprocessing import Process
from datetime import datetime

# Flask App Initialization
app = Flask(__name__)

@app.route("/")
def index():
    return "Flask server is running successfully!"

# Replace with your Bot Token and Channel ID
BOT_TOKEN = "7202087814:AAHUpeC_uXQ54VwJkZtwMzGa4juGEGAJmkg"
CHANNEL_ID = "-1002313229856"
ADMIN_USER_ID = 5181364124
GROUP_LINK = "https://t.me/+zfuv4O9ZDuU0ZTVl"

bot = Bot(token=BOT_TOKEN)
posting_active = False  # Flag to track if predictions are being posted

# API URL and headers for fetching results
DATA_LIST_URL = "https://api.bdg88zf.com/api/webapi/GetNoaverageEmerdList"
HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*"
}

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Generate period code based on time
def generate_period_code():
    calendar = time.gmtime()
    total_minutes = calendar.tm_hour * 60 + calendar.tm_min
    period_code = f"{time.strftime('%Y%m%d', calendar)}1000{10001 + total_minutes}"
    return period_code

# Fetch result from API
def fetch_result_from_api(period_code):
    try:
        payload = {
            "pageSize": 10,
            "pageNo": 1,
            "typeId": 1,
            "language": 0,
            "random": "ded40537a2ce416e96c00e5218f6859a",
            "signature": "69306982EEEB19FA940D72EC93C62552",
            "timestamp": int(datetime.now().timestamp())
        }

        response = requests.post(DATA_LIST_URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            result_data = response.json()
            for item in result_data.get("data", []):
                if item.get("periodCode") == period_code:
                    return item.get("result")
        else:
            logging.error(f"API request failed with status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error fetching result from API: {e}")
    return None

# Prediction task
async def send_prediction():
    global posting_active
    while True:
        if posting_active:
            try:
                period_code = generate_period_code()
                last_5_digits = period_code[-5:]
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

                sent_message = await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="HTML")
                await asyncio.sleep(30)

                result_from_api = fetch_result_from_api(period_code)

                final_status = "RESULT NOT FOUND" if result_from_api is None else (
                    "WIN" if prediction == ("BIG" if 5 <= result_from_api <= 9 else "SMALL") else "LOSS"
                )

                updated_message = (
                    f"❤️🔥 <b>Prediction:</b>\n\n"
                    f"🕹 <b>Game:</b> Wingo 1 Min\n\n"
                    f"📟 <b>Period Number:</b> {period_code}\n\n"
                    f"🎰 <b>Prediction:</b> 🍤 {prediction} 🍤\n\n"
                    f"Last 5 Digits: <b>{last_5_digits}</b>\n\n"
                    f"<b>STATUS:</b> {final_status}\n\n"
                    f"✅ Make your own bot DM: @TANMAYPAUL21"
                )
                await bot.edit_message_text(chat_id=CHANNEL_ID, message_id=sent_message.message_id, text=updated_message, parse_mode="HTML")
                await asyncio.sleep(60 - time.gmtime().tm_sec)
            except Exception as e:
                logging.error(f"Error in send_prediction: {e}")
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text(f"The BOT IS ONLY AVAILABLE IN THIS GROUP: {GROUP_LINK}")
    else:
        await update.message.reply_text("Welcome to the Prediction Bot!")

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global posting_active
    if update.effective_user.id == ADMIN_USER_ID:
        posting_active = True
        await update.message.reply_text("Bot started posting predictions.")
    else:
        await update.message.reply_text("You are not authorized.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global posting_active
    if update.effective_user.id == ADMIN_USER_ID:
        posting_active = False
        await update.message.reply_text("Bot stopped posting predictions.")
    else:
        await update.message.reply_text("You are not authorized.")

async def prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# Run Flask and Bot together
def run_flask():
    app.run(host="0.0.0.0", port=10000)

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prediction", prediction))
    application.add_handler(CommandHandler("post", post))
    application.add_handler(CommandHandler("stop", stop))
    asyncio.run(send_prediction())
    application.run_polling()

if __name__ == "__main__":
    flask_process = Process(target=run_flask)
    flask_process.start()
    run_bot()
