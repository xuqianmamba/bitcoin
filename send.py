import socket
import json
from blockchain.transaction import Transaction
from ecdsa import SigningKey, NIST384p

# 假设我们有一个已知的节点地址和端口
node_address = "localhost"
node_port = 5000

def send_transaction_to_node(node, port, transaction):
    """向指定的节点发送交易"""
    transaction_data = json.dumps(transaction.to_dict()).encode('utf-8')  # 使用to_dict方法
    # transaction_data = json.dumps(transaction.__dict__).encode('utf-8')  # 将交易转换为JSON格式
    print(transaction.from_address)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((node, port))
            s.send("SEND".encode('utf-8'))
            s.send(transaction_data)
            # response = s.recv(1024)
            # print(f"Received response: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error sending transaction to {node}:{port}: {e}")

# 示例：创建一个交易并发送
# sender_sk = SigningKey.generate(curve=NIST384p)
# # sender_sk =
# with open("priv_key.pem", "wb") as f:
#     f.write(sender_sk.to_pem(format="pkcs8"))
with open("priv_key.pem") as f:
    sender_sk = SigningKey.from_pem(f.read())
print("wallet",sender_sk.to_string().hex())
sender_vk = sender_sk.verifying_key
receiver_sk = SigningKey.generate(curve=NIST384p)
receiver_vk = receiver_sk.verifying_key

# 创建交易
transaction = Transaction(sender_vk.to_string().hex(), receiver_vk.to_string().hex(), 10)
transaction.sign_transaction(sender_sk)  # 假设Transaction类有一个方法来签名交易


# 发送交易
send_transaction_to_node(node_address, node_port, transaction)
