from ecdsa import SigningKey, NIST384p

# 如果 Block 和 Blockchain 类都在 block.py 里
from blockchain.block import Block, Blockchain
from blockchain.transaction import Transaction
from blockchain.merkle_tree import merkle_root

# 生成发送者和接收者的密钥对
sender_sk = SigningKey.generate(curve=NIST384p)
sender_vk = sender_sk.verifying_key
receiver_sk = SigningKey.generate(curve=NIST384p)
receiver_vk = receiver_sk.verifying_key

# 创建交易
transaction1 = Transaction(sender_vk.to_string().hex(), receiver_vk.to_string().hex(), 10)
transaction1.sign_transaction(sender_sk)

transaction2 = Transaction(receiver_vk.to_string().hex(), sender_vk.to_string().hex(), 5)
transaction2.sign_transaction(receiver_sk)

# 初始化区块链并添加交易
my_blockchain = Blockchain()
my_blockchain.add_transaction(transaction1)
my_blockchain.add_transaction(transaction2)

# 挖矿以添加新区块
my_blockchain.mine_pending_transactions(receiver_vk.to_string().hex())

# 打印区块链信息来验证
for block in my_blockchain.chain:
    print(f"区块索引: {block.index}")
    print(f"区块时间戳: {block.timestamp}")
    print(f"区块交易: {block.transactions}")
    print(f"区块随机数Nonce: {block.nonce}")
    print(f"上一个区块的哈希: {block.previous_hash}")
    print(f"区块哈希: {block.hash}")
    print(f"默克尔根: {block.merkle_root}")
    print("----------")
