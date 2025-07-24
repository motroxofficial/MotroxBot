import sqlite3
from datetime import datetime
from config import PROFIT_RATE

def init_db():
    conn = sqlite3.connect('motrox.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  join_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS investments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  amount REAL,
                  deposit_date TEXT,
                  last_profit_calc TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS withdrawals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  amount REAL,
                  address TEXT,
                  request_date TEXT,
                  status TEXT DEFAULT 'pending',
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('motrox.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?)",
              (user_id, username, first_name, last_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def add_investment(user_id, amount):
    conn = sqlite3.connect('motrox.db')
    c = conn.cursor()
    c.execute("INSERT INTO investments (user_id, amount, deposit_date, last_profit_calc) VALUES (?, ?, ?, ?)",
              (user_id, amount, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = sqlite3.connect('motrox.db')
    c = conn.cursor()
    c.execute("SELECT amount, deposit_date, last_profit_calc FROM investments WHERE user_id=?", (user_id,))
    investments = c.fetchall()
    
    total = 0
    for inv in investments:
        amount = inv[0]
        last_calc = datetime.fromisoformat(inv[2])
        hours_passed = (datetime.now() - last_calc).total_seconds() / 3600
        profit_periods = hours_passed / 2
        profit = amount * (1 + PROFIT_RATE) ** profit_periods - amount
        total += amount + profit
    
    conn.close()
    return total

def request_withdrawal(user_id, amount, address):
    conn = sqlite3.connect('motrox.db')
    c = conn.cursor()
    c.execute("INSERT INTO withdrawals (user_id, amount, address, request_date) VALUES (?, ?, ?, ?)",
              (user_id, amount, address, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_pending_withdrawals():
    conn = sqlite3.connect('motrox.db')
    c = conn.cursor()
    c.execute("SELECT * FROM withdrawals WHERE status='pending'")
    withdrawals = c.fetchall()
    conn.close()
    return withdrawals

def update_withdrawal_status(withdrawal_id, status):
    conn = sqlite3.connect('motrox.db')
    c = conn.cursor()
    c.execute("UPDATE withdrawals SET status=? WHERE id=?", (status, withdrawal_id))
    conn.commit()
    conn.close()