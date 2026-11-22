import datetime
import hashlib
import json
import sqlite3


# ------------------ DB CONNECTION ------------------
def get_db():
    conn = sqlite3.connect("blockchain.db", timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):

        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions.copy()
        }

        block['hash'] = self.hash(block)

        self.transactions = []
        self.chain.append(block)

        # ✅ SAFE DB WRITE
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO blocks (data) VALUES (?)",
                (json.dumps(block),)
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print("DB Error:", e)

        return block

    def get_previous_block(self): #returns last block in chain
        return self.chain[-1]

    def proof_of_work(self, previous_proof): # performs mining
        new_proof = 1
        while True:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()
            ).hexdigest()

            if hash_operation[:4] == '0000':
                return new_proof
            new_proof += 1

    def hash(self, block): # converts blocks data into hash
        block_copy = block.copy()
        block_copy.pop('hash', None)
        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):

        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]

            if current['previous_hash'] != previous['hash']:
                return False

            if current['hash'] != self.hash(current):
                return False

        return True

    def add_transaction(self, sender, receiver, product):

        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'product': product
        })

        # ✅ SAFE DB WRITE
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO transactions (sender, receiver, product) VALUES (?, ?, ?)",
                (sender, receiver, product)
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print("DB Error:", e)

        return self.get_previous_block()['index'] + 1