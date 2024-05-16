import threading
import socket
import json
import time
from blockchain.transaction import Transaction
from blockchain.block import Block, Blockchain
from ecdsa import SigningKey, NIST384p
from blockchain.block import Block, Blockchain,create_chain_from_dict,create_block_from_dict,create_transaction_from_data

def block_md5(sth):
    return 0

def sign_header(a1,a2):
    return 0

def check_sign_header(a1,a2):
    return True

class Node:
    def __init__(self, node_id, is_faulty=False):
        self.sender_sk = SigningKey()
        self.sender_vk = self.sender_sk.verifying_key
        self.node_id = node_id
        self.is_faulty = is_faulty
        self.nodes = []
        self.messages = []
        self.blockchain = Blockchain()
        self.lock = Lock()
        self.prepare_count = 0
        self.commit_count = 0
    def send_message(self, message, nodes):
        for node in nodes:
            node.receive_message(message)
        print(f"Node {self.node_id}: Sent message {message}")

    def receive_message(self, message):
        if not self.is_faulty:
            self.messages.append(message)
            print(f"Node {self.node_id}: Received message {message}")
        else:
            # 模拟拜占庭行为，可能篡改消息或不做任何事
            if random.choice([True, False]):
                self.messages.append(message)
                print(f"Node {self.node_id} (Faulty): Received and kept message {message}")
            else:
                print(f"Node {self.node_id} (Faulty): Received and discarded message {message}")

    def send_block_to_node(self,header,id,node, port, block):
        """向指定的节点发送更新块"""
        # print(type(block))
        # block_data = json.dumps(block.to_dict()).encode('utf-8')  # 使用to_dict方法
        
        hash_block = block_md5(block)
        header_dict = {"header":header,"id":id,"hash_block":hash_block,"pubkey":self.sender_vk.to_string().to_hex()}
        signed_header = sign_header(header_dict,self.sender_sk)
        
        data_dict = {"block_dict":block.to_dict(),"signed_header":signed_header,"header_dict" : header_dict}
        send_data = json.dumps(data_dict).encode('utf-8')
        # block_data = json.dumps(block.__dict__).encode('utf-8')  # 将交易转换为JSON格式
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node, port))
                s.send(send_data)
                # response = s.recv(1024)
                # print(f"Received response: {response.decode('utf-8')}")
        except Exception as e:
            print(f"Error sending block to {node}:{port}: {e}")
    def handle_client_connection(self,client_socket, address):
        try:
            msg_data = client_socket.recv(1024*1024*1024) 
            data_dict = json.loads(msg_data.decode("utf-8"))
            header_dict = data_dict["header_dict"]
            header = header_dict["header"]
        except Exception as e:
            print(f"Error receving header")
            return
        print(f"Received message from {address}: {message}")
        if header.startswith("REQUEST"):
            if not check_sign_header(data_dict["header_dict"],data_dict["signed_header"]):
                print(f"find sign error in the transaction")
            else:
                if not self.blockchain.add_transaction(data_dict["block_dict"]) :
                    print(f"error in transcation")
                elif len(blockchain.pending_transactions) == 5 :
                    with self.blockchain.lock:
                        self.blockchain.pending_transactions.append(Transaction(None, self.node_id, self.blockchain.mining_reward))
                        block = Block(len(self.blockchain.chain), self.blockchain.pending_transactions, time.time(), self.blockchain.get_last_block().hash)
                        self.blockchain.pending_transactions = []
                    
                    header = "PRE-PREPARE"
                    block = self.blockchain.get_last_block()
                    threads = []
                    for node in nodes:
                        now_thread = threading.Thread(target=send_block_to_node, args=(self,header,node_id,node,5000,block))
                        threads.append(now_thread)
                    for thread in threads:
                        thread.start()
                    
                    with self.lock:
                        self.prepare_count = 1
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(('0.0.0.0', port))
                    server_socket.listen(5)
                    print(f"Listening on port {port}...")


                    for node in self.nodes:
                        with self.lock:
                            if self.prepare_count == 3:
                                break
                        client_sock, address = server_socket.accept()
                        print(f"Accepted connection from {address}")
                        handle_client_connection(self,client_sock, address)
                    
                    server_socket.close()

                    header = "COMMIT"
                    threads = []
                    for node in nodes:
                        now_thread = threading.Thread(target=send_block_to_node, args=(self,header,node_id,node,5000,block))
                        threads.append(now_thread)
                    for thread in threads:
                        thread.start()
                    
                    with self.lock:
                        self.commit_count = 1
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(('0.0.0.0', port))
                    server_socket.listen(5)
                    print(f"Listening on port {port}...")


                    for node in self.nodes:
                        with self.lock:
                            if self.commit_count == 3:
                                break
                        client_sock, address = server_socket.accept()
                        print(f"Accepted connection from {address}")
                        handle_client_connection(self,client_sock, address)
                    server_socket.close()
        elif header.startswith("PRE-PREPARE"):
            if not check_sign_header(data_dict["header_dict"],data_dict["signed_header"]):
                print(f"find sign error in the transaction")
            else:
                if not self.blockchain.add_transaction(data_dict["block_dict"]) :
                    print(f"error in transcation")
                elif len(blockchain.pending_transactions) == 5 :
                    with self.blockchain.lock:
                        self.blockchain.pending_transactions.append(Transaction(None, self.node_id, self.blockchain.mining_reward))
                        block = Block(len(self.blockchain.chain), self.blockchain.pending_transactions, time.time(), self.blockchain.get_last_block().hash)
                        self.blockchain.pending_transactions = []
                    
                    header = "PREPARE"
                    block = self.blockchain.get_last_block()
                    threads = []
                    for node in nodes:
                        now_thread = threading.Thread(target=send_block_to_node, args=(self,header,node_id,node,5000,block))
                        threads.append(now_thread)
                    for thread in threads:
                        thread.start()
                    
                    with self.lock:
                        self.prepare_count = 2
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(('0.0.0.0', port))
                    server_socket.listen(5)
                    print(f"Listening on port {port}...")

                    for node in self.nodes:
                        with self.lock:
                            if self.prepare_count == 3:
                                break
                        client_sock, address = server_socket.accept()
                        print(f"Accepted connection from {address}")
                        handle_client_connection(self,client_sock, address)
                    server_socket.close()

                    header = "COMMIT"
                    threads = []
                    for node in nodes:
                        now_thread = threading.Thread(target=send_block_to_node, args=(self,header,node_id,node,5000,block))
                        threads.append(now_thread)
                    for thread in threads:
                        thread.start()
                    
                    with self.lock:
                        self.commit_count = 1
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(('0.0.0.0', port))
                    server_socket.listen(5)
                    print(f"Listening on port {port}...")

                    for node in self.nodes:
                        with self.lock:
                            if self.commit_count == 3:
                                break
                        client_sock, address = server_socket.accept()
                        print(f"Accepted connection from {address}")
                        handle_client_connection(self,client_sock, address)
                    server_socket.close()
        elif header.startswith("PREPARE"):
            if not header_dict["hash_block"] == block_md5(self.my_blockchain.get_last_block()):
                return
            with self.lock:
                self.prepare_count += 1
        
        
        elif header.startswith("COMMIT"):
            if not header_dict["hash_block"] == block_md5(self.my_blockchain.get_last_block()):
                return
            with self.lock:
                self.commit_count += 1

                    




class PBFTNode(Node):
    def __init__(self, node_id, is_faulty=False):
        super().__init__(node_id, is_faulty)
        self.prepared = False
        self.committed = False  # 确保每个节点都初始化 committed 属性

    def pre_prepare(self, request, nodes):
        self.send_message(('PRE-PREPARE', request), nodes)

    def prepare(self, request, nodes):
        if self.messages.count(('PRE-PREPARE', request)) > 0:
            self.send_message(('PREPARE', request), nodes)

    def commit(self, request, nodes):
        prepare_count = self.messages.count(('PREPARE', request))
        if prepare_count > len(nodes) // 2:#+pre-prepare
            self.send_message(('COMMIT', request), nodes)

    def execute(self, request):
        commit_count = self.messages.count(('COMMIT', request))
        if commit_count > len(nodes) // 2:#+pre-prepare
            self.committed = True
            print(f"Node {self.node_id}: Executed request: {request}")

def leader_server(node,port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Listening on port {port}...")
    
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

if __name__ == '__main__':
    node = Node()
    leader_server(node,7777)

# nodes = [PBFTNode(i) for i in range(4)]
# nodes.append(PBFTNode(4, is_faulty=True))  # 添加一个拜占庭节点

# primary_node = nodes[0]
# primary_node.pre_prepare("transaction1", nodes)

# for node in nodes:
#     node.prepare("transaction1", nodes)
#     node.commit("transaction1", nodes)

# for node in nodes:
#     if hasattr(node, 'committed') and node.committed:
#         node.execute("transaction1")

# def test_pbft():
#     print("Testing PBFT with correct message...")
#     nodes = [PBFTNode(i) for i in range(4)]
#     nodes.append(PBFTNode(4, is_faulty=True))  # 添加一个拜占庭节点
#     primary_node = nodes[0]
#     primary_node.pre_prepare("test_transaction", nodes)

#     for node in nodes:
#         node.prepare("test_transaction", nodes)
#         node.commit("test_transaction", nodes)

#     for node in nodes:
#         if hasattr(node, 'committed') and node.committed:
#             node.execute("test_transaction")

# test_pbft()



# def handle_client_connection(client_socket, address):
#     # 接收客户端发送的消息
#     message = client_socket.recv(4).decode('utf-8')
#     if not message:
#         return  # 客户端关闭连接
    
#     print(f"Received message from {address}: {message}")
    
#     # 根据收到的消息类型执行不同的操作
#     if message == 'SEND':
#         # 接收后续的交易数据
#         transaction_data_bytes = client_socket.recv(1024 * 1024)  # 假设交易数据不会超过1024字节
#         transaction_data_str = transaction_data_bytes.decode('utf-8')
#         transaction_data = json.loads(transaction_data_str)  # 将JSON字符串反序列化为字典

#          # 使用接收到的信息创建一个新的Transaction对象
#         new_transaction = create_transaction_from_data(transaction_data)

#         # 如果交易数据中包含timestamp和signature，可以在这里设置
#         # 注意：在实际应用中，你可能需要验证签名的有效性
#         # if 'timestamp' in transaction_data:
#         #     new_transaction.timestamp = transaction_data['timestamp']
#         # if 'signature' in transaction_data and transaction_data['signature']:
#         #     new_transaction.signature = bytes.fromhex(transaction_data['signature'])
#         if my_blockchain.add_transaction(new_transaction):
#             print("新交易创建成功")
#         else:
#             print("新交易创建失败")

#         if len(my_blockchain.pending_transactions) == 5:
#             mine_pending_transactions_PBFT("10.77.110.166")
