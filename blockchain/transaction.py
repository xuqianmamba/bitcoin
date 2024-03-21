import hashlib
import time
class Transaction:
    #交易有没有判别法
    def __init__(self, from_address, to_address, amount,timestamp = time.time()):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.timestamp = timestamp 
        self.signature = ""
    def __eq__(self, other):
        if not isinstance(other, Transaction):
            # 不与非Transaction类型比较
            return NotImplemented
        return (self.from_address == other.from_address and
                self.to_address == other.to_address and
                self.amount == other.amount and
                self.timestamp == other.timestamp)
    def calculate_hash(self):
        transaction_string = f"{self.from_address}{self.to_address}{self.amount}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, signing_key):
        # 将验证密钥转换为十六进制字符串
        if signing_key.verifying_key.to_string().hex() != self.from_address:
            raise Exception("You cannot sign transactions for other wallets!")
        hash_tx = self.calculate_hash()
        self.signature = signing_key.sign(hash_tx.encode())

    def is_valid(self):
        if self.from_address == None:
            return True
        if not self.signature or len(self.signature) == 0:
            raise Exception("No signature in this transaction")
        # Verification logic here
        return True
    
    def to_dict(self):
        return {
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature.hex() if self.signature else None
        }
