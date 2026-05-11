import hashlib
import json
from datetime import datetime
from config import Config
import os
from database import get_db_connection

class Block:
    def __init__(self, index, timestamp, action, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.action = action
        self.data = data  # dict
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "action": self.action,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "action": self.action,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self, file_path=Config.BLOCKCHAIN_FILE):
        self.file_path = file_path
        self.chain = []
        self.load_chain()
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            action="GENESIS",
            data={"message": "Genesis Block"},
            previous_hash="0"
        )
        self.chain.append(genesis.to_dict())
        self.save_chain()
        self._persist_block_to_db(genesis)

    def add_block(self, action, data):
        previous = self.chain[-1]
        index = previous['index'] + 1
        timestamp = datetime.utcnow().isoformat()
        previous_hash = previous['hash']
        block = Block(index, timestamp, action, data, previous_hash)
        self.chain.append(block.to_dict())
        self.save_chain()
        self._persist_block_to_db(block)
        return block.to_dict()

    def is_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            # check prev hash link
            if curr['previous_hash'] != prev['hash']:
                return False
            # verify hash integrity
            recalculated = hashlib.sha256(json.dumps({
                "index": curr['index'],
                "timestamp": curr['timestamp'],
                "action": curr['action'],
                "data": curr['data'],
                "previous_hash": curr['previous_hash']
            }, sort_keys=True).encode()).hexdigest()
            if curr['hash'] != recalculated:
                return False
        return True

    def load_chain(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.chain = data
            except Exception:
                self.chain = []
        else:
            self.chain = []

    def save_chain(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(self.chain, f, indent=4)

    def _persist_block_to_db(self, block_obj):
        """Save block to DB blocks table. block_obj can be Block or dict."""
        try:
            b = block_obj.to_dict() if hasattr(block_obj, "to_dict") else block_obj
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO blocks (block_index, timestamp, action, data_json, previous_hash, hash) VALUES (%s, %s, %s, %s, %s, %s)",
                (b['index'], b['timestamp'], b['action'], json.dumps(b['data']), b['previous_hash'], b['hash'])
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            # Log error but don't fail the block creation (block is already saved to JSON)
            print(f"Warning: Failed to persist block to database: {str(e)}")
            # Ensure connection is closed even on error
            try:
                if 'conn' in locals() and conn.is_connected():
                    conn.close()
            except:
                pass