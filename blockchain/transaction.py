import hashlib
class Transaction:
    #交易有没有判别法
    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.signature = ""

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
