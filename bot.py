# bot.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import asyncio
import json
import os

OWNER_ID = 7845994060  # Your Telegram ID
BOT_TOKEN = "7509938357:AAEXVLbk0cdud8qgX8R-O50dYFepNrVz6oU"
USDT_ADDRESS = "TTP45gJWhuo6Axe8jYqc1hBc2f8zMyS5Ki"
DATA_FILE = "users.json"

# Load or create data file
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

with open(DATA_FILE, "r") as f:
    users = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

def calculate_profit(join_time, amount):
    hours_passed = (asyncio.get_event_loop().time() - join_time) // 7200  # 2 hours
    return round(amount * (0.008 * hours_passed), 2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    if user_id not in users:
        users[user_id] = {
            "name": user.first_name,
            "joined": asyncio.get_event_loop().time(),
            "amount": 0,
            "withdraw_request": False,
            "wallet": ""
        }
        save_data()

    keyboard = [
        [InlineKeyboardButton("📥 Deposit", callback_data="deposit")],
        [InlineKeyboardButton("📈 Progress", callback_data="progress")],
        [InlineKeyboardButton("💰 Withdraw", callback_data="withdraw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"👋 Welcome {user.first_name} to Motrox Bot!", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == "deposit":
        users[user_id]["joined"] = asyncio.get_event_loop().time()
        save_data()
        await query.edit_message_text(f"💳 Send USDT TRC20 to:\n\n`{USDT_ADDRESS}`\n\n⏱ Profit: 0.8% every 2 hours.", parse_mode='Markdown')

    elif query.data == "progress":
        user = users.get(user_id, {})
        profit = calculate_profit(user.get("joined", 0), user.get("amount", 0))
        await query.edit_message_text(f"📊 Investment Progress:\nAmount: {user.get('amount', 0)} USDT\nProfit: {profit} USDT")

    elif query.data == "withdraw":
        users[user_id]["withdraw_request"] = True
        save_data()
        await query.edit_message_text("💼 Please send your USDT wallet address to withdraw.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if users.get(user_id, {}).get("withdraw_request"):
        users[user_id]["wallet"] = text
        users[user_id]["withdraw_request"] = False
        save_data()

        await update.message.reply_text("✅ Withdrawal request sent to admin.")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"💸 Withdraw request from {user_id}:\nWallet: {text}")
    else:
        await update.message.reply_text("❓ Use the menu buttons to interact.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
