from blockchain.block import Block, Blockchain,create_chain_from_dict,create_block_from_dict,create_transaction_from_data
from blockchain.transaction import Transaction
from ecdsa import SigningKey, NIST384p
from blockchain.merkle_tree import merkle_root
import socket
import threading
import time
from queue import Queue
from threading import Lock
import json

from wallet.wallet import Wallet

# 创建一个锁对象
lock = Lock()
my_wallet =  Wallet() 


# def mine_transactions():
#     while True:
#         with lock:
#             if transactionPool:
#                 print("发现待处理的交易，开始挖矿...")
#                 # 复制transactionPool中的所有待处理的交易
#                 transactions = transactionPool.copy()
#                 # 清空transactionPool
#                 transactionPool.clear()

#         # 假设mine_pending_transactions方法接受一个交易列表作为参数
#         # 注意：挖矿操作和广播不应在持有锁的情况下进行，以避免不必要的阻塞
#         new_block = my_blockchain.mine_pending_transactions(transactions)
#         # 假设broadcast_block方法用于广播新挖掘的区块
#         my_blockchain.broadcast_block(new_block)
#         print("新区块已广播")

#         # 每秒检查一次
#         time.sleep(1)



def handle_client_connection(client_socket, address):
    # 接收客户端发送的消息
    message = client_socket.recv(4).decode('utf-8')  # 修改接收长度为1024，以确保能接收完整的消息
    if not message:
        return  # 客户端关闭连接
    
    print(f"Received message from {address}: {message}")
    
    # 根据收到的消息类型执行不同的操作
    if message == 'SEND':
        # 接收后续的交易数据
        transaction_data_bytes = client_socket.recv(1024)  # 假设交易数据不会超过1024字节
        transaction_data_str = transaction_data_bytes.decode('utf-8')
        transaction_data = json.loads(transaction_data_str)  # 将JSON字符串反序列化为字典

         # 使用接收到的信息创建一个新的Transaction对象
        new_transaction = create_transaction_from_data(transaction_data)

        # 如果交易数据中包含timestamp和signature，可以在这里设置
        # 注意：在实际应用中，你可能需要验证签名的有效性
        # if 'timestamp' in transaction_data:
        #     new_transaction.timestamp = transaction_data['timestamp']
        # if 'signature' in transaction_data and transaction_data['signature']:
        #     new_transaction.signature = bytes.fromhex(transaction_data['signature'])
        my_blockchain.add_transaction(new_transaction)
        print("新交易创建成功")

    elif message.startswith('UPDT'):
        # 这里添加更新区块链的逻辑
        # print(json.dumps(my_blockchain.to_dict()).encode('utf-8'))
        client_socket.send(json.dumps(my_blockchain.to_dict()).encode('utf-8'))
        
        pass
    elif message.startswith('MINE'):
        # 这里添加挖矿的逻辑
        # 接收后续的交易数据
        block_data_bytes = client_socket.recv(1024*1024)  # 假设交易数据不会超过1024字节
        block_data_str = block_data_bytes.decode('utf-8')
        block_data = json.loads(block_data_str)  # 将JSON字符串反序列化为字典

        # 使用接收到的信息创建一个新的block对象
        new_block = create_block_from_dict(block_data)
        ok = False
        if not any(b.hash == new_block.hash for b in my_blockchain.chain):
            if new_block.previous_hash == my_blockchain.get_last_block().hash:
                if my_blockchain.calculate_hash()[:my_blockchain.difficulty] == '0' * my_blockchain.difficulty:
                    my_state = WalletState(my_blockchain)
                    cnt = 0
                    for transaction in new_block.transactions:
                        if my_state.add_transaction(transaction):
                            cnt += 1
                        else:
                            break
                    if cnt == len(new_block.transactions):
                        ok = True
        if ok:
            with my_blockchain.lock:
                my_blockchain.chains.append(new_block)
                new_list = []
                for transaction in my_blockchain.pending_transactions:
                    if transaction not in new_block.transactions:
                        new_list.append(transaction)
                my_blockchain.pending_transactions = new_list
    else:
        print("Unknown command!")
    # 可以根据需要添加更多的条件分支
    
    # 发送响应给客户端
    # client_socket.sendall("ACK".encode('utf-8'))
    
    client_socket.close()
def mining(interval):
    while True:
        my_blockchain.mine_pending_transactions(my_wallet.public_key.to_string().hex())
        print("I'm mining")
        time.sleep(interval)  # 等待指定的时间间隔（秒）

def schedule_chain_queries(interval):
    while True:
        my_blockchain.update_chains()
        time.sleep(interval)  # 等待指定的时间间隔（秒）

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Listening on port {port}...")
    
    # 创建并启动询问最长链的线程
    chain_query_thread = threading.Thread(target=schedule_chain_queries, args=(10,))
    chain_query_thread.start()
    

    mining_thread = threading.Thread(target=mining, args=(3,))
    mining_thread.start()
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

# # 创建交易
# transaction1 = Transaction(sender_vk.to_string().hex(), receiver_vk.to_string().hex(), 10)
# transaction1.sign_transaction(sender_sk)

# transaction2 = Transaction(receiver_vk.to_string().hex(), sender_vk.to_string().hex(), 5)
# transaction2.sign_transaction(receiver_sk)

# # 添加交易到交易池
# my_blockchain.add_transaction(transaction1)
# my_blockchain.add_transaction(transaction2)

# # 挖矿
# my_blockchain.mine_pending_transactions(receiver_vk.to_string().hex())



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