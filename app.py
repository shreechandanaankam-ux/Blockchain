from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
from datetime import datetime
import os

from blockchain import Blockchain
from routes.transaction_routes import add_transaction
from routes.block_routes import mine_block, get_chain
from routes.utility_routes import tamper, is_valid, track_product

app = Flask(__name__)
app.secret_key = "secret123"

blockchain = Blockchain()

DB = "blockchain.db"


# ------------------ DB CONNECTION ------------------
def get_db():
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ------------------ RESET ------------------
@app.route('/reset')
def reset_blockchain():
    global blockchain
    blockchain = Blockchain()

    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

    return "Blockchain reset successfully!"


# ------------------ HOME ------------------
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')


# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hour = datetime.now().hour

        # 🚫 STEP 1: CHECK IF USER IS BLOCKED
        c.execute("SELECT * FROM hackers WHERE session_id=?", (username,))
        is_hacker = c.fetchone()

        if is_hacker:
            conn.close()
            return "🚫 Access Denied! You are blocked as a hacker."

        # 🔐 STEP 2: CHECK USER CREDENTIALS
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()

        # ✅ SUCCESS LOGIN
        if user:
            c.execute("INSERT INTO login_attempts (username, status, time) VALUES (?, ?, ?)",
                      (username, "SUCCESS", current_time))
            conn.commit()

            session['user'] = username
            conn.close()
            return redirect('/')

        # ❌ FAILED LOGIN
        c.execute("INSERT INTO login_attempts (username, status, time) VALUES (?, ?, ?)",
                  (username, "FAILED", current_time))
        conn.commit()

        # COUNT FAILURES
        c.execute("SELECT COUNT(*) FROM login_attempts WHERE username=? AND status='FAILED'",
                  (username,))
        failed_count = c.fetchone()[0]

        # 🚨 MARK AS HACKER
        if failed_count >= 3:
            c.execute("INSERT INTO hackers (session_id, reason) VALUES (?, ?)",
                      (username, "3 failed attempts"))
            conn.commit()

            blockchain.add_transaction("System", "Admin",
                                       f"Hacker detected: {username}")

            conn.close()
            return "🚫 You are now permanently blocked as HACKER!"

        # ⚠️ SUSPICIOUS TIME CHECK
        if 0 <= hour <= 4:
            c.execute("INSERT INTO hackers (session_id, reason) VALUES (?, ?)",
                      (username, "Login at suspicious time"))
            conn.commit()

            blockchain.add_transaction("System", "Admin",
                                       f"Suspicious login: {username}")

            conn.close()
            return "⚠️ Suspicious login detected!"

        conn.close()
        return "Invalid login!"

    return render_template('login.html')
@app.route('/blocked_dashboard')
def blocked_dashboard():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT session_id, reason FROM hackers")
    data = c.fetchall()

    conn.close()

    return render_template("blocked_dashboard.html", data=data)


# ------------------ REGISTER ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, password))

        conn.commit()
        conn.close()

        return "User Registered! Go to login page"

    return render_template('register.html')


# ------------------ BLOCKCHAIN ROUTES ------------------
@app.route('/add_transaction', methods=['POST'])
def handle_add_transaction():
    return add_transaction(blockchain)


@app.route('/mine_block')
def handle_mine_block():
    return mine_block(blockchain)


@app.route('/get_chain')
def handle_get_chain():
    return get_chain(blockchain)


@app.route('/tamper')
def handle_tamper():
    return tamper(blockchain)


@app.route('/is_valid')
def handle_is_valid():
    return is_valid(blockchain)


@app.route('/track')
def handle_track():
    product = request.args.get('product')
    return track_product(blockchain, product)


# ------------------ VIEW DB ------------------
@app.route('/view_db')
def view_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    data = c.fetchall()
    conn.close()
    return str(data)


# ------------------ FLOW DATA ------------------
@app.route('/flow_data')
def flow_data():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT sender, receiver FROM transactions")
    data = c.fetchall()
    conn.close()

    nodes = set()
    edges = []

    for sender, receiver in data:
        nodes.add(sender)
        nodes.add(receiver)
        edges.append({"from": sender, "to": receiver})

    return jsonify({"nodes": list(nodes), "edges": edges})


# ------------------ VIEW HACKERS ------------------
@app.route('/view_hackers')
def view_hackers():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT session_id, reason FROM hackers")
    data = c.fetchall()
    conn.close()

    return render_template("hackers.html", data=data)
@app.route('/run_dataset')
def run_dataset():
    os.system("python dataset_analysis.py")
    return "✅ Dataset analyzed successfully!"


# ------------------ DETECT HACKERS ------------------
@app.route('/detect_hackers')
def detect_hackers():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    # Clear old hackers
   

    # Get dataset
    c.execute("SELECT * FROM dataset")
    data = c.fetchall()

    def safe_int(val):
        try:
            return int(val)
        except:
            return 0

    for row in data:

        session_id = row["session_id"]

        login_attempts = safe_int(row["login_attempts"])
        failed_logins = safe_int(row["failed_logins"])
        browser = str(row["browser_type"])
        unusual_time = safe_int(row["unusual_time_access"])
        attack = safe_int(row["attack_detected"])

        reason_list = []

        if failed_logins >= 2:
            reason_list.append("High failed logins")

        if login_attempts >= 4:
           reason_list.append("Too many login attempts")

        if attack == 1:
            reason_list.append("Attack detected")

# WEAK CONDITIONS (only count if combined)
        if browser.lower() == "unknown":
            reason_list.append("Unknown browser")

        if unusual_time == 1:
            reason_list.append("Unusual time login")


# ✅ FINAL DECISION
        if len(reason_list) >= 2:
           for reason in reason_list:
               c.execute(
               "INSERT INTO hackers (session_id, reason) VALUES (?, ?)",
            (session_id, reason)
        )

    # ✅ FIRST close DB
    conn.commit()
    conn.close()

    # ✅ THEN blockchain (only once)
    blockchain.add_transaction(
        sender="Dataset",
        receiver="Security",
        product="Dataset analysis completed"
    )

    return "✅ Dataset analysis completed! Hackers detected."


# ------------------ CHART ------------------
@app.route('/chart_data')
def chart_data():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT reason, COUNT(*) FROM hackers GROUP BY reason")
    data = c.fetchall()

    conn.close()

    return jsonify({
        "labels": [row[0] for row in data],
        "values": [row[1] for row in data]
    })


# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)