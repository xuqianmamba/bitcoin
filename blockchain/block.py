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

def create_transaction_from_data(transaction_data):
    """
    根据提供的交易数据创建一个新的Transaction对象。

    参数:
    - transaction_data: 包含交易数据的字典，应包括from_address, to_address和amount字段。

    返回:
    - 一个新的Transaction对象。
    """
    new_transaction = Transaction(
        from_address=transaction_data['from_address'],
        to_address=transaction_data['to_address'],
        amount=transaction_data['amount'],
        timestamp=transaction_data['timestamp']
    )
    # 如果交易数据中还包含其他字段，如timestamp和signature，可以在这里添加相应的处理逻辑
    # 例如:
    # if 'timestamp' in transaction_data:
    #     new_transaction.timestamp = transaction_data['timestamp']
    new_transaction.signature = bytes.fromhex(transaction_data['signature']) if transaction_data['signature'] else None
    return new_transaction

def create_block_from_dict(block_data):
    """
    根据提供的字典数据创建一个新的Block对象。

    参数:
    - block_data: 包含区块数据的字典，应包括index, transactions, timestamp, previous_hash, nonce, merkle_root和hash字段。

    返回:
    - 一个新的Block对象。
    """
    # 首先，将transactions列表中的每个字典转换为Transaction对象
    transactions = [Transaction(
        tx_data['from_address'],
        tx_data['to_address'],
        tx_data['amount']  # 假设字典中可能包含可选的signature字段
    ) for tx_data in block_data['transactions']]
    
    # 创建Block对象
    new_block = Block(
        index=block_data['index'],
        transactions=transactions,
        timestamp=block_data['timestamp'],
        previous_hash=block_data['previous_hash'],
        nonce=block_data['nonce']
    )
    # 由于Block构造函数中不直接设置merkle_root和hash，我们在这里手动设置
    new_block.merkle_root = block_data['merkle_root']
    new_block.hash = block_data['hash']

    return new_block

def create_chain_from_dict(chain_data):
    """
    根据提供的字典数据创建一个新的Blockchain对象。

    参数:
    - chain_data: 包含整个区块链数据的字典，应包括chain, difficulty, pending_transactions, mining_reward字段。

    返回:
    - 一个新的Blockchain对象。
    """
    # 创建一个空的Blockchain对象
    new_blockchain = Blockchain()
    new_blockchain.chain = []  # 清空初始链
    new_blockchain.difficulty = chain_data['difficulty']
    new_blockchain.mining_reward = chain_data['mining_reward']
    
    # 将字典中的每个区块转换为Block对象并添加到链中
    for block_dict in chain_data['chain']:
        block = create_block_from_dict(block_dict)
        new_blockchain.chain.append(block)
    
    # 将待处理的交易转换为Transaction对象并添加到待处理交易列表中
    new_blockchain.pending_transactions = [
        Transaction(tx['from_address'], tx['to_address'], tx['amount']) 
        for tx in chain_data['pending_transactions']
    ]
    
    return new_blockchain

# class Node:
#     def __init__(self, host, port, blockchain):
#         self.host = host
#         self.port = port
#         self.blockchain = blockchain
#         self.peers = []  # 存储已知的网络节点

#     def start_server(self):
#         t = threading.Thread(target=self._server)
#         t.start()

#     def _server(self):
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         server_socket.bind((self.host, self.port))
#         server_socket.listen()

#         while True:
#             conn, address = server_socket.accept()
#             client_thread = threading.Thread(target=self.handle_client, args=(conn,))
#             client_thread.start()

#     def handle_client(self, connection):
#         while True:
#             data = connection.recv(1024)
#             if not data:
#                 break
            
#             # 假设收到的数据是其他节点的区块链
#             received_blockchain = Blockchain.from_json(data.decode())
#             self.blockchain.resolve_conflicts([received_blockchain])

#         connection.close()

#     def connect_with_node(self, host, port):
#         self.peers.append((host, port))

#     def send_blockchain_to_peers(self):
#         for peer in self.peers:
#             try:
#                 client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 client_socket.connect(peer)
#                 client_socket.send(self.blockchain.to_json().encode())
#                 client_socket.close()
#             except Exception as e:
#                 print(f"Connection to peer {peer} failed: {e}")

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
    
    def to_dict(self):
        """将区块转换为字典形式，以便于序列化。"""
        return {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root,
            'hash': self.hash,
        }

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 1
        self.pending_transactions = []
        self.mining_reward = 100
        self.lock = Lock()  # 在这里添加一个锁对象
        self.nodes = {'localhost'}  # 假设'localhost'代表当前节点或默认节点


    def create_genesis_block(self):
        return Block(0, [], time.time(), "0")

    def get_last_block(self):
        return self.chain[-1]

    def send_block_to_node(self,node, port, block):
        """向指定的节点发送交易"""
        print(type(block))
        block_data = json.dumps(block.to_dict()).encode('utf-8')  # 使用to_dict方法
        # block_data = json.dumps(block.__dict__).encode('utf-8')  # 将交易转换为JSON格式
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node, port))
                s.send("MINE".encode('utf-8'))
                s.send(block_data)
                # response = s.recv(1024)
                # print(f"Received response: {response.decode('utf-8')}")
        except Exception as e:
            print(f"Error sending block to {node}:{port}: {e}")
    
    def update_chains(self):
        neighbor_chains = [self]
        for node in self.nodes:
            updated_chain = self.update_chains_from_node(node)
            # if updated_chain is not None:  # 确保返回的是有效的Blockchain对象
            neighbor_chains.append(updated_chain)
        return self.resolve_conflicts(neighbor_chains)


    def update_chains_from_node(self,node, port=5000):
        """向指定的节点发送整个区块链"""
        chain_data = json.dumps(self.to_dict()).encode('utf-8')  # 使用to_dict方法将整个区块链转换为JSON格式
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node, port))
                s.send("UPDT".encode('utf-8'))  # 发送一个标识符，让接收方知道这是一个区块链数据

                chain_data = s.recv(1024*1024).decode('utf-8')

                chain_data = json.loads(chain_data)
                
                return create_chain_from_dict(chain_data)
                # response = s.recv(1024)
                # print(f"Received response: {response.decode('utf-8')}")
        except Exception as e:
            print(f"Error sending chain to {node}:{port}: {e}")

    def mine_pending_transactions(self, mining_reward_address):
        # 创建新区块
        with self.lock:
            self.pending_transactions.append(Transaction(None, mining_reward_address, self.mining_reward))
            block = Block(len(self.chain), self.pending_transactions, time.time(), self.get_last_block().hash)
            self.pending_transactions = []
        # 执行工作量证明算法
        block.nonce = self.proof_of_work(block)
        block.hash  = block.calculate_hash()
        # 检查区块链中是否已存在该nonce
        if not any(b.hash == block.hash for b in self.chain):
            print(f"Block successfully mined! Hash: {block.hash}")
            self.chain.append(block)
            # print("out",block.to_dict())
            for node_ in self.nodes:
                self.send_block_to_node(node_,5000,block)
            # self.pending_transactions = [Transaction(None, mining_reward_address, self.mining_reward).to_dict()]
        else:
            print("Mining result already exists, discarding the result.")

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.calculate_hash()
        #这里要break 并且返回
        while computed_hash[:self.difficulty] != '0' * self.difficulty:
            block.nonce += 1
            computed_hash = block.calculate_hash()
        # print("in",block.to_dict())
        return block.nonce

    def add_transaction(self, transaction):
        # Here should be validation checks for the transaction
        with self.lock:
            self.pending_transactions.append(transaction)
        print(transaction.to_dict())
        return True
    
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
            print(chain)
            if len(chain.chain) > max_length and self.is_chain_valid(chain.chain):
                max_length = len(chain.chain)
                longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False
    
    def to_dict(self):
        """将整个区块链转换为字典形式，包括每个区块和区块链的其他属性。"""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'difficulty': self.difficulty,
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'mining_reward': self.mining_reward,
        }