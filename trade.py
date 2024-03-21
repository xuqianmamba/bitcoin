from blockchain.block import Block, Blockchain
from blockchain.transaction import Transaction
from ecdsa import SigningKey, NIST384p
from blockchain.merkle_tree import merkle_root
import socket
import threading
import time
from queue import Queue
from threading import Lock

# 创建一个锁对象
lock = Lock()


def mine_transactions():
    while True:
        with lock:
            if transactionPool:
                print("发现待处理的交易，开始挖矿...")
                # 复制transactionPool中的所有待处理的交易
                transactions = transactionPool.copy()
                # 清空transactionPool
                transactionPool.clear()

        # 假设mine_pending_transactions方法接受一个交易列表作为参数
        # 注意：挖矿操作和广播不应在持有锁的情况下进行，以避免不必要的阻塞
        new_block = my_blockchain.mine_pending_transactions(transactions)
        # 假设broadcast_block方法用于广播新挖掘的区块
        my_blockchain.broadcast_block(new_block)
        print("新区块已广播")

        # 每秒检查一次
        time.sleep(1)

def handle_client_connection(client_socket):
    # 接收客户端发送的消息
    message = client_socket.recv(1024).decode('utf-8')
    if not message:
        return  # 客户端关闭连接
    
    print(f"Received message: {message}")
    
    # 根据收到的消息类型执行不同的操作
    if message.startswith('SEND_BLOCK'):
        # 这里添加处理发送区块到区块链的逻辑
        pass
    elif message.startswith('UPDATE_BLOCKCHAIN'):
        # 这里添加更新区块链的逻辑
        pass
    elif message.startswith('MINE'):
        # 这里添加挖矿的逻辑
        pass
    else:
        print("yes!")
    # 可以根据需要添加更多的条件分支
    
    # 发送响应给客户端
    client_socket.sendall("ACK".encode('utf-8'))
    
    client_socket.close()

def query_longest_chain():
    # 这里是向所有节点询问最长链的逻辑
    print("正在询问最长链...")
    # 假设这里有代码向所有已知的节点发送请求，并处理它们的回应

def schedule_chain_queries(interval):
    while True:
        query_longest_chain()
        time.sleep(interval)  # 等待指定的时间间隔（秒）

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Listening on port {port}...")
    
    # 创建并启动询问最长链的线程
    chain_query_thread = threading.Thread(target=schedule_chain_queries, args=(60,))  # 每60秒询问一次
    chain_query_thread.start()
    
    try:
        while True:
            client_sock, address = server_socket.accept()
            print(f"Accepted connection from {address}")
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock, address)
            )
            client_handler.start()
    finally:
        server_socket.close()


# 初始化
my_blockchain = Blockchain()

# 假设这是网络中接收到的其它节点的链
neighbor_chains = []

# 在这里我们可能会从网络中接收其它节点的区块链版本
# 为了模拟，我们将手动添加一些区块链
# 在实际应用中，这些信息会通过网络传输
# neighbor_chains.append(other_blockchain.chain)

# 解决冲突，选择最长的有效链
if my_blockchain.resolve_conflicts(neighbor_chains):
    print("我们的链被替换了")
else:
    print("我们的链是权威的")

# 生成密钥对
sender_sk = SigningKey.generate(curve=NIST384p)
sender_vk = sender_sk.verifying_key
receiver_sk = SigningKey.generate(curve=NIST384p)
receiver_vk = receiver_sk.verifying_key

# 创建交易
transaction1 = Transaction(sender_vk.to_string().hex(), receiver_vk.to_string().hex(), 10)
transaction1.sign_transaction(sender_sk)

transaction2 = Transaction(receiver_vk.to_string().hex(), sender_vk.to_string().hex(), 5)
transaction2.sign_transaction(receiver_sk)

# 添加交易到交易池
my_blockchain.add_transaction(transaction1)
my_blockchain.add_transaction(transaction2)

# 挖矿
my_blockchain.mine_pending_transactions(receiver_vk.to_string().hex())



#一个节点向另一个节点要blockchain长什么样
#1.发送block，更新blockchain
#2.发送/恢复blockchain
#3.挖矿，返回一个结果，可能会连接到



#4.blockchain要加一个判断，要判断一个人账户不能为负数，要根据


# 打印区块链信息来验证
for block in my_blockchain.chain:
    print(f"区块索引: {block.index}")
    print(f"区块时间戳: {block.timestamp}")
    print(f"区块交易: {block.transactions}")
    print(f"区块随机数Nonce: {block.nonce}")
    print(f"上一个区块的哈希: {block.previous_hash}")
    print(f"区块哈希: {block.hash}")
    # print(f"默克尔


if __name__ == '__main__':
    PORT = 5000  # 选择一个端口号
    start_server(PORT)