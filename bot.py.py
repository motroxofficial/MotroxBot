import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID, USDT_ADDRESS, PROFIT_RATE
from database import *
from datetime import datetime
import time

bot = telebot.TeleBot(BOT_TOKEN)
init_db()

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("What we do?", callback_data="what_we_do"),
        InlineKeyboardButton("Deposit", callback_data="deposit"),
        InlineKeyboardButton("Withdraw", callback_data="withdraw"),
        InlineKeyboardButton("Balance", callback_data="balance"),
        InlineKeyboardButton("Progress", callback_data="progress")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_user(message.from_user.id, message.from_user.username, 
            message.from_user.first_name, message.from_user.last_name)
    
    welcome_msg = """🌟 *Welcome to Motrox Investment Bot* 🌟

🚀 *Your path to daily profits with USDT TRC-20!*

• Earn *10-15% daily returns* on your investment
• Simple and secure process
• Fast withdrawals

Use the buttons below to navigate:"""
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "what_we_do":
        what_we_do(call.message)
    elif call.data == "deposit":
        deposit(call.message)
    elif call.data == "withdraw":
        withdraw(call.message)
    elif call.data == "balance":
        balance(call.message)
    elif call.data == "progress":
        progress(call.message)

def what_we_do(message):
    msg = """📈 *What Motrox Does?*

Motrox is an advanced investment bot that generates profits for you:

• Invest using *USDT TRC-20*
• Earn *10-15% daily returns*
• Automatic profit calculation
• Secure and transparent

Minimum deposit: *10 USDT*
Maximum deposit: *No limit*

Your funds work for you 24/7!"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=main_menu())

def deposit(message):
    msg = f"""💵 *Deposit USDT TRC-20*

To make a deposit, send USDT (TRC-20) to the following address:

`{USDT_ADDRESS}`

*Important:*
1. Only send USDT on the TRON network (TRC-20)
2. Send from your personal wallet (no exchange wallets)
3. Minimum deposit: 10 USDT

After sending, your balance will update automatically within 15 minutes."""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=main_menu())

def withdraw(message):
    msg = """💸 *Withdraw Funds*

Please enter your USDT TRC-20 address where you want to receive funds:"""
    sent = bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    bot.register_next_step_handler(sent, process_withdraw_address)

def process_withdraw_address(message):
    address = message.text.strip()
    msg = "Now enter the amount you want to withdraw:"
    sent = bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    bot.register_next_step_handler(sent, process_withdraw_amount, address)

def process_withdraw_amount(message, address):
    try:
        amount = float(message.text)
        user_balance = get_user_balance(message.from_user.id)
        
        if amount > user_balance:
            bot.send_message(message.chat.id, "❌ Insufficient balance!", reply_markup=main_menu())
            return
        
        request_withdrawal(message.from_user.id, amount, address)
        admin_msg = f"⚠️ New Withdrawal Request\n\nUser: @{message.from_user.username}\nAmount: {amount} USDT\nAddress: {address}"
        bot.send_message(ADMIN_ID, admin_msg)
        bot.send_message(message.chat.id, "✅ Withdrawal request submitted! It will be processed within 24 hours.", 
                         reply_markup=main_menu())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Please enter a valid number!", reply_markup=main_menu())

def balance(message):
    balance = get_user_balance(message.from_user.id)
    msg = f"""💰 *Your Balance*

Current balance: *{balance:.2f} USDT*
Estimated daily profit: *{balance * 0.12:.2f} USDT* (12%)

Your balance grows automatically every 2 hours!"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=main_menu())

def progress(message):
    msg = """📊 *Investment Progress*

Your investment grows by *0.8% every 2 hours* (approximately *10-15% daily*).

Current rate: *0.8% per 2 hours*
Compounding effect: *Yes*

Example:
- $100 becomes $108 after 24 hours
- $1000 becomes $1080 after 24 hours"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['admin'], func=lambda message: message.from_user.id == ADMIN_ID)
def admin_panel(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Pending Withdrawals", callback_data="pending_withdrawals"))
    bot.send_message(message.chat.id, "Admin Panel:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pending_withdrawals")
def show_pending_withdrawals(call):
    withdrawals = get_pending_withdrawals()
    if not withdrawals:
        bot.send_message(call.message.chat.id, "No pending withdrawals.")
        return
    for wd in withdrawals:
        wd_id, user_id, amount, address, request_date, status = wd
        msg = f"""Withdrawal #{wd_id}
User: {user_id}
Amount: {amount} USDT
Address: {address}
Date: {request_date}

/approve_{wd_id} /reject_{wd_id}"""
        bot.send_message(call.message.chat.id, msg)

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text.startswith('/approve_'))
def approve_withdrawal(message):
    try:
        wd_id = int(message.text.split('_')[1])
        update_withdrawal_status(wd_id, "approved")
        bot.send_message(message.chat.id, f"Withdrawal #{wd_id} approved!")
    except:
        bot.send_message(message.chat.id, "Invalid command")

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text.startswith('/reject_'))
def reject_withdrawal(message):
    try:
        wd_id = int(message.text.split('_')[1])
        update_withdrawal_status(wd_id, "rejected")
        bot.send_message(message.chat.id, f"Withdrawal #{wd_id} rejected!")
    except:
        bot.send_message(message.chat.id, "Invalid command")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()