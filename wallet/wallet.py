from ecdsa import SigningKey, NIST384p
class Wallet:
    def __init__(self):
        self.public_key = SigningKey.generate(curve=NIST384p)
        self.prvate_key = self.public_key.verifying_key
        self.account = self.public_key