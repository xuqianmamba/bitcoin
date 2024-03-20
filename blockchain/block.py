from .merkle_tree import merkle_root
from .transaction import Transaction
import time
import hashlib

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = merkle_root([tx.calculate_hash() for tx in transactions])
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.merkle_root}{self.timestamp}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []
        self.mining_reward = 100

    def create_genesis_block(self):
        return Block(0, [], time.time(), "0")

    def get_last_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        block = Block(len(self.chain), self.pending_transactions, time.time(), self.get_last_block().hash)
        block.nonce = self.proof_of_work(block)
        print(f"Block successfully mined! Hash: {block.hash}")
        self.chain.append(block)
        self.pending_transactions = [{"from_address": None, "to_address": mining_reward_address, "amount": self.mining_reward}]

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.calculate_hash()
        while computed_hash[:self.difficulty] != '0' * self.difficulty:
            block.nonce += 1
            computed_hash = block.calculate_hash()
        return block.nonce

    def add_transaction(self, transaction):
        # Here should be validation checks for the transaction
        self.pending_transactions.append(transaction)