import os
import time
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler, ContextTypes

TOKEN = "7509938357:AAEXVLbk0cdud8qgX8R-O50dYFepNrVz6oU"
ADMIN_ID = 7845994060
USDT_ADDRESS = "TTP45gJWhuo6Axe8jYqc1hBc2f8zMyS5Ki"

users = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_time(seconds):
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {sec}s"

async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0.0, "last_profit_time": datetime.now(), "deposited": False}
    keyboard = [
        [InlineKeyboardButton("💸 Deposit", callback_data='deposit')],
        [InlineKeyboardButton("📈 Progress", callback_data='progress')],
        [InlineKeyboardButton("💰 Balance", callback_data='balance')],
        [InlineKeyboardButton("🏧 Withdraw", callback_data='withdraw')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 Welcome to Motrox Investment Bot!", reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in users:
        users[user_id] = {"balance": 0.0, "last_profit_time": datetime.now(), "deposited": False}

    data = users[user_id]
    now = datetime.now()

    if query.data == "deposit":
        await query.edit_message_text(
            f"📥 To deposit, send USDT (TRC20) to this address:

`{USDT_ADDRESS}`

Then click /confirm once done.",
            parse_mode='Markdown'
        )

    elif query.data == "progress":
        elapsed = now - data["last_profit_time"]
        await query.edit_message_text(
            f"⏳ Time since last profit: {format_time(elapsed.total_seconds())}

"
            f"💰 Balance: {data['balance']:.2f} USDT"
        )

    elif query.data == "balance":
        await query.edit_message_text(f"💼 Your current balance is: {data['balance']:.2f} USDT")

    elif query.data == "withdraw":
        if data["balance"] <= 0:
            await query.edit_message_text("❌ You have no balance to withdraw.")
        else:
            await query.edit_message_text("✅ Withdrawal request sent to admin. You will be contacted soon.")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"📤 User {user_id} requested withdrawal of {data['balance']:.2f} USDT")
            data["balance"] = 0.0

async def confirm(update: Update, context: CallbackContext.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in users:
        users[user_id]["deposited"] = True
        users[user_id]["last_profit_time"] = datetime.now()
        await update.message.reply_text("✅ Deposit confirmed. You will start earning profits every 2 hours.")
    else:
        await update.message.reply_text("❌ Please use /start first.")

async def profit_task(app):
    import asyncio
    while True:
        now = datetime.now()
        for user_id, data in users.items():
            if data["deposited"] and (now - data["last_profit_time"]) >= timedelta(hours=2):
                data["balance"] += data["balance"] * 0.008 if data["balance"] > 0 else 0.8
                data["last_profit_time"] = now
        await asyncio.sleep(60)

if __name__ == '__main__':
    import asyncio
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("confirm", confirm))
    app.job_queue.run_once(lambda *_: asyncio.create_task(profit_task(app)), 1)
    app.run_polling()