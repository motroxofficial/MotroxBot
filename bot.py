
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Command
from datetime import datetime, timedelta

API_TOKEN = "7509938357:AAEXVLbk0cdud8qgX8R-O50dYFepNrVz6oU"
ADMIN_ID = 7845994060
USDT_ADDRESS = "TTP45gJWhuo6Axe8jYqc1hBc2f8zMyS5Ki"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users = {}

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    users[message.from_user.id] = {"balance": 0, "deposits": [], "last_profit_time": datetime.now()}
    await message.answer(f"👋 Welcome to *Motrox Investment Bot*!

💸 To deposit, send USDT (TRC20) to this address:
`{USDT_ADDRESS}`", parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(commands=["deposit"])
async def deposit_handler(message: types.Message):
    await message.answer(f"💸 Send your USDT (TRC20) deposit to this address:

`{USDT_ADDRESS}`", parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(commands=["balance"])
async def balance_handler(message: types.Message):
    user = users.get(message.from_user.id)
    if not user:
        await message.answer("❌ You have no account yet. Send /start")
        return

    # Calculate profits every 2 hours
    now = datetime.now()
    last = user["last_profit_time"]
    hours = int((now - last).total_seconds() // 7200)
    if hours > 0:
        profit = user["balance"] * 0.008 * hours
        user["balance"] += profit
        user["last_profit_time"] = now

    await message.answer(f"💼 Your current balance is: ${user['balance']:.2f}")

@dp.message_handler(commands=["withdraw"])
async def withdraw_handler(message: types.Message):
    await message.answer("📤 Withdrawal feature coming soon.")

@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    total_users = len(users)
    total_balance = sum(u["balance"] for u in users.values())
    await message.answer(f"🛠 Admin Panel
👥 Users: {total_users}
💰 Total Balance: ${total_balance:.2f}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
