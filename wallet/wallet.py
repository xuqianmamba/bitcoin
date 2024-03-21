from ecdsa import SigningKey, NIST384p
class Wallet:
    def __init__(self):

        # self.public_key = SigningKey.generate(seed,curve=NIST384p)
        with open("priv_key.pem") as f:
            self.private_key = SigningKey.from_pem(f.read())
        print("wallet",self.private_key.to_string().hex())
        self.public_key = self.private_key.verifying_key
        # self.account = self.public_key