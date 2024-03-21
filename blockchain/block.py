from .merkle_tree import merkle_root
from .transaction import Transaction
import time
import hashlib
import socket
import threading
import json
import sys
from threading import Lock
# from blockchain.block import Block, Blockchain
from blockchain.transaction import Transaction
from blockchain.merkle_tree import merkle_root

class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = []  # 存储已知的网络节点

    def start_server(self):
        t = threading.Thread(target=self._server)
        t.start()

    def _server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        while True:
            conn, address = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(conn,))
            client_thread.start()

    def handle_client(self, connection):
        while True:
            data = connection.recv(1024)
            if not data:
                break
            
            # 假设收到的数据是其他节点的区块链
            received_blockchain = Blockchain.from_json(data.decode())
            self.blockchain.resolve_conflicts([received_blockchain])

        connection.close()

    def connect_with_node(self, host, port):
        self.peers.append((host, port))

    def send_blockchain_to_peers(self):
        for peer in self.peers:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(peer)
                client_socket.send(self.blockchain.to_json().encode())
                client_socket.close()
            except Exception as e:
                print(f"Connection to peer {peer} failed: {e}")

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
        self.lock = Lock()  # 在这里添加一个锁对象

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
        #这里要break 并且返回
        while computed_hash[:self.difficulty] != '0' * self.difficulty:
            block.nonce += 1
            computed_hash = block.calculate_hash()
        return block.nonce

    def add_transaction(self, transaction):
        # Here should be validation checks for the transaction
        with self.lock:
            self.pending_transactions.append(transaction)
    
    def is_chain_valid(self, chain):
        # 检查链是否有效
        for i in range(1, len(chain)):
            current_block = chain[i]
            prev_block = chain[i - 1]

            # 检查区块的哈希是否正确
            if current_block.hash != current_block.calculate_hash():
                return False

            # 检查区块是否链接至上一个区块
            if current_block.previous_hash != prev_block.calculate_hash():
                return False

            # 这里还可以添加其他的检查，比如交易的有效性等

        return True

    def resolve_conflicts(self, neighbor_chains):
        # 用于网络共识，解决链的冲突，选择最长的有效链
        longest_chain = None
        max_length = len(self.chain)

        for chain in neighbor_chains:
            if len(chain) > max_length and self.is_chain_valid(chain):
                max_length = len(chain)
                longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False