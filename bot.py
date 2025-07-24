import os
import time
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
USDT_ADDRESS = os.getenv("USDT_ADDRESS")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.reply("🤖 Welcome to Motrox!\n\n💸 To deposit, send USDT (TRC20) to this address:\n\n" + USDT_ADDRESS + "\n\nAfter deposit, click /progress to track your profits.\nUse /withdraw to request withdrawal.")

@dp.message_handler(commands=['progress'])
async def progress(msg: types.Message):
    user_id = msg.from_user.id
    if user_id not in user_data:
        await msg.reply("❌ No deposit found.")
        return

    deposit = user_data[user_id]["deposit"]
    start_time = user_data[user_id]["start_time"]
    hours_passed = (time.time() - start_time) / 3600
    earnings = deposit * 0.008 * (hours_passed // 2)

    await msg.reply(f"💰 Deposit: {deposit} USDT\n⏱ Time Passed: {int(hours_passed)} hours\n📈 Earnings: {earnings:.2f} USDT")

@dp.message_handler(commands=['deposit'])
async def deposit(msg: types.Message):
    user_id = msg.from_user.id
    if user_id != ADMIN_ID:
        await msg.reply("❌ Only admin can add deposits.")
        return

    args = msg.text.split()
    if len(args) != 3:
        await msg.reply("Usage: /deposit user_id amount")
        return

    uid = int(args[1])
    amt = float(args[2])
    user_data[uid] = {"deposit": amt, "start_time": time.time()}
    await msg.reply(f"✅ Deposit added for user {uid}")

@dp.message_handler(commands=['withdraw'])
async def withdraw(msg: types.Message):
    user_id = msg.from_user.id
    if user_id not in user_data:
        await msg.reply("❌ No deposit found.")
        return

    await msg.reply("📤 Withdrawal request sent to admin.")

    await bot.send_message(
        ADMIN_ID,
        f"🔔 User {user_id} has requested a withdrawal.\nDeposit: {user_data[user_id]['deposit']} USDT"
    )

if __name__ == '__main__':
    executor.start_polling(dp)
