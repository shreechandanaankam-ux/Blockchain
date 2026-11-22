import sqlite3
import pandas as pd
import os
print("DB path:", os.path.abspath("blockchain.db")) 

# connect database
conn = sqlite3.connect("blockchain.db")
cursor = conn.cursor()

# load csv
df = pd.read_csv("cybersecurity_intrusion_data.csv")

# print to check (IMPORTANT)
print(df.head())

# create table
# automatically create table based on dataset
columns = ", ".join(df.columns)
placeholders = ", ".join(["?"] * len(df.columns))

cursor.execute("DROP TABLE IF EXISTS dataset")

cursor.execute(f"CREATE TABLE dataset ({columns})")

# insert all rows
for i in range(len(df)):
    cursor.execute(
        f"INSERT INTO dataset VALUES ({placeholders})",
        tuple(df.iloc[i])
    )

conn.commit()

# check count
cursor.execute("SELECT COUNT(*) FROM dataset")
print("Inserted rows:", cursor.fetchone())

conn.close()

print("✅ DONE")