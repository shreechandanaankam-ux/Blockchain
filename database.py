import sqlite3

def init_db():
    conn = sqlite3.connect('blockchain.db') #connects to sqlite database
    cursor = conn.cursor()

    # Transactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        product TEXT
    )
    ''')

    # Blocks Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT
    )
    ''')

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    # Login Attempts Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        status TEXT,
        time TEXT
    )
    ''')

    # Hackers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hackers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        reason TEXT
    )
    ''')

    conn.commit()
    conn.close()