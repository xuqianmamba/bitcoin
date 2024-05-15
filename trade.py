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
from wallet.walletstate import WalletState
# 创建一个锁对象
lock = Lock()
my_wallet =  Wallet() 


def handle_client_connection(client_socket, address):
    # 接收客户端发送的消息
    message = client_socket.recv(4).decode('utf-8')
    if not message:
        return  # 客户端关闭连接
    
    print(f"Received message from {address}: {message}")
    
    # 根据收到的消息类型执行不同的操作
    if message == 'SEND':
        # 接收后续的交易数据
        transaction_data_bytes = client_socket.recv(1024 * 1024)  # 假设交易数据不会超过1024字节
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
        if my_blockchain.add_transaction(new_transaction):
            print("新交易创建成功")
        else:
            print("新交易创建失败")


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
        cnt = 0
        # print("my_blockchain.chain",type(my_blockchain.chain))
        # for b in my_blockchain.chain:
        #     print(b.to_dict(),b.hash == new_block.hash)
        # print(any(b.hash == new_block.hash for b in my_blockchain.chain))
        print(new_block.index,my_blockchain.get_last_block().index)
        if not any(b.hash == new_block.hash for b in my_blockchain.chain):
            print("nonce ok")
            if new_block.previous_hash == my_blockchain.get_last_block().hash:
                print("previous hash ok")
                if my_blockchain.calculate_hash()[:my_blockchain.difficulty] == '0' * my_blockchain.difficulty:
                    print("difficulty ok")
                    my_state = WalletState(my_blockchain)
                    for transaction in new_block.transactions:
                        if my_state.add_transaction(transaction):
                            cnt += 1
                        else:
                            break
                    if cnt == len(new_block.transactions):
                        ok = True
        
        if ok:
            print("ok",my_state.wallet_map)
            with my_blockchain.lock:
                my_blockchain.chains.append(new_block)
                new_list = []
                for transaction in my_blockchain.pending_transactions:
                    if transaction not in new_block.transactions:
                        new_list.append(transaction)
                my_blockchain.pending_transactions = new_list
        else:
            print("Fail",f"{cnt}/{len(new_block.transactions)}")
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
    # chain_query_thread = threading.Thread(target=schedule_chain_queries, args=(10,))
    # chain_query_thread.start()
    

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


if __name__ == '__main__':
    PORT = 5000  # 选择一个端口号
    start_server(PORT)