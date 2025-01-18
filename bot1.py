import logging
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

@app.route('/')
def index():
    return "Flask server is running successfully!"

def start_flask():
    app.run(host="0.0.0.0", port=10000)

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Replace with your Bot Token and Channel ID
BOT_TOKEN = "7078882104:AAGoZovCt-7wloK-9RFefQ9flc-Lf06if08"  # Replace with your Bot Token
CHANNEL_ID = "-1002408621955"  # Replace with your Channel ID
ADMIN_USER_ID = 6105849915  # Replace with your admin's Telegram user ID
GROUP_LINK = "https://t.me/+houBGxe-Xq5mNDll"  # Replace with your group's link

bot = Bot(token=BOT_TOKEN)
posting_active = False  # Flag to track if predictions are being posted

# Function to generate period code based on the current time
def generate_period_code():
    calendar = time.gmtime()
    total_minutes = calendar.tm_hour * 60 + calendar.tm_min
    period_code = f"{time.strftime('%Y%m%d', calendar)}1000{10001 + total_minutes}"
    return period_code

# Prediction Calculation Functions

def calculate_prediction(last_3_digits):
    # Reverse Digit Sum
    def reverse_digit_sum(period_number):
        return sum(int(digit) for digit in reversed(period_number)) % 10

    # Digit Alternation
    def digit_alternation(period_number):
        return (int(period_number[0]) + int(period_number[2]) - int(period_number[1])) % 10

    # Squared Sum
    def squared_sum(period_number):
        return sum(int(digit)**2 for digit in period_number) % 10

    # Modulus Product
    def modulus_product(period_number):
        return (int(period_number[0]) * int(period_number[1]) * int(period_number[2])) % 7

    # Binary Conversion
    def binary_conversion(period_number):
        binary = bin(int(period_number))[2:]
        return sum(int(bit) for bit in binary) % 10

    # Digit Rotation
    def digit_rotation(period_number):
        rotated = period_number[1:] + period_number[0]
        return sum(int(digit) for digit in rotated) % 10

    # Exponential Sum
    def exponential_sum(period_number):
        return sum(int(digit)**3 for digit in period_number) % 10

    # Fibonacci Weighted Sum
    def fibonacci_weighted_sum(period_number):
        fib_weights = [1, 1, 2]
        return sum(int(period_number[i]) * fib_weights[i] for i in range(3)) % 10

    # Prime Number Check
    def prime_number_check(n):
        if n <= 1:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        max_div = int(n**0.5) + 1
        for i in range(3, max_div, 2):
            if n % i == 0:
                return False
        return True

    # Hash Function
    def hash_function(n):
        return (n * 1103515245 + 12345) % 2**31

    # Convert the period code to the last 3 digits and calculate the prediction
    prediction_value = reverse_digit_sum(last_3_digits)
    
    # You can replace the logic here with other functions as needed (e.g., use other prediction logic)
    if prediction_value >= 5:
        return "BIG"
    else:
        return "SMALL"

# Send prediction message to channel
async def send_prediction():
    global posting_active
    while True:
        if posting_active:
            try:
                # Generate the period code
                period_code = generate_period_code()
                last_3_digits = period_code[-3:]  # Extract last 3 digits
                prediction = calculate_prediction(last_3_digits)

                # Prepare the message
                message = (
                    f"❤️🔥 <b>Prediction:</b>\n\n"
                    f"🕹 <b>Game:</b> Wingo 1 Min\n\n"
                    f"📟 <b>Period Number:</b> {period_code}\n\n"
                    f"🎰 <b>Prediction:</b> 🍤 {prediction} 🍤\n\n"
                    f"Last 3 Digits: <b>{last_3_digits}</b>\n\n"
                    f"<b>STATUS:</b> WAITING FOR RESULT\n\n"
                    f"✅ Make your own bot DM: @BN_OWNER"
                )

                # Send the initial prediction message to the channel
                sent_message = await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="HTML")
                await asyncio.sleep(30)

                # Mock result for demonstration purposes
                actual_result = "BIG" if int(last_3_digits) % 2 == 0 else "SMALL"
                final_status = "WIN" if prediction == actual_result else "LOSS"

                # Update the message with the final result
                updated_message = (
                    f"❤️🔥 <b>Prediction:</b>\n\n"
                    f"🕹 <b>Game:</b> Wingo 1 Min\n\n"
                    f"📟 <b>Period Number:</b> {period_code}\n\n"
                    f"🎰 <b>Prediction:</b> 🍤 {prediction} 🍤\n\n"
                    f"Last 3 Digits: <b>{last_3_digits}</b>\n\n"
                    f"<b>STATUS:</b> {final_status}\n\n"
                    f"✅ Make your own bot DM: @BN_OWNER"
                )

                await bot.edit_message_text(chat_id=CHANNEL_ID, message_id=sent_message.message_id, text=updated_message, parse_mode="HTML")
                await asyncio.sleep(60)

            except Exception as e:
                logging.error(f"Error in prediction cycle: {e}")
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text(f"The BOT IS ONLY AVAILABLE IN THIS GROUP: {GROUP_LINK}")
    else:
        await update.message.reply_text(
            "Welcome to the Prediction Bot!\n\n"
            "Commands:\n"
            "/post - Start posting predictions (admin only).\n"
            "/stop - Stop posting predictions (admin only).\n"
            "/prediction - Show the next prediction."
        )

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global posting_active
    if update.effective_user.id == ADMIN_USER_ID:
        posting_active = True
        await update.message.reply_text("Bot will now start posting predictions.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global posting_active
    if update.effective_user.id == ADMIN_USER_ID:
        posting_active = False
        await update.message.reply_text("Bot has stopped posting predictions.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

async def prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    period_code = generate_period_code()
    last_3_digits = period_code[-3:]
    prediction = calculate_prediction(last_3_digits)

    message = (
        f"❤️🔥 <b>Prediction:</b>\n\n"
        f"🕹 <b>Game:</b> Wingo 1 Min\n\n"
        f"📟 <b>Period Number:</b> {period_code}\n\n"
        f"🎰 <b>Prediction:</b> 🍤 {prediction} 🍤\n\n"
        f"Last 3 Digits: <b>{last_3_digits}</b>\n\n"
        f"✅ Make your own bot DM: @BN_OWNER"
    )

    await update.message.reply_text(message, parse_mode="HTML")

# Main Bot Runner
def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("post", post))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("prediction", prediction))

    asyncio.get_event_loop().create_task(send_prediction())
    application.run_polling()

if __name__ == "__main__":
    flask_process = Process(target=start_flask)
    flask_process.start()
    run_bot()
