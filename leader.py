import random
from blockchain.block import Block, Blockchain,create_chain_from_dict,create_block_from_dict,create_transaction_from_data
def send_block_to_node(self,header,id,node, port, block):
    """向指定的节点发送更新块"""
    # print(type(block))
    # block_data = json.dumps(block.to_dict()).encode('utf-8')  # 使用to_dict方法
    
    hash_block = md5(block_data)
    header_dict = {"header":header,"id":id,"hash_block":hash_block}
    signed_header = sign_header(header,sender_sk)
    
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

    
class Node:
    def __init__(self, node_id, is_faulty=False):
        self.node_id = node_id
        self.is_faulty = is_faulty
        self.messages = []

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

        if len(my_blockchain.pending_transactions) == 5:
            mine_pending_transactions_PBFT("10.77.110.166")
