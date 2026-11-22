import pandas as pd
import sqlite3

# load dataset
df = pd.read_csv("cybersecurity_intrusion_data.csv") #reads dataset,detetct hackers,store results

conn = sqlite3.connect("blockchain.db")
cursor = conn.cursor()

for index, row in df.iterrows():

    session = row['session_id']
    login_attempts = row['login_attempts']
    failed_logins = row['failed_logins']
    unusual_time = row['unusual_time']
    attack = row['attack_detected']

    # 🚨 condition 1: multiple login attempts
    if login_attempts >= 3:
        cursor.execute(
            "INSERT INTO hackers (session_id, reason) VALUES (?, ?)",
            (session, "Multiple login attempts")
        )

    # 🚨 condition 2: failed password attempts
    if failed_logins >= 3:
        cursor.execute(
            "INSERT INTO hackers (session_id, reason) VALUES (?, ?)",
            (session, "3+ failed passwords")
        )

    # 🚨 condition 3: suspicious time
    if unusual_time == 1:
        cursor.execute(
            "INSERT INTO hackers (session_id, reason) VALUES (?, ?)",
            (session, "Login at unusual time")
        )

    # 🚨 condition 4: already detected attack
    if attack == 1:
        cursor.execute(
            "INSERT INTO hackers (session_id, reason) VALUES (?, ?)",
            (session, "Attack detected by system")
        )

conn.commit()
conn.close()

print("✅ Hackers detected from dataset!")