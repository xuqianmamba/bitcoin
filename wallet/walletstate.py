
from blockchain.block import Block, Blockchain
from blockchain.transaction import Transaction
class WalletState:
    def __init__(self,blockchain = None,wallet_map = None):
        self.is_valid = True
        if wallet_map is not None:
            self.wallet_map = wallet_map
        else:
            self.wallet_map = dict()
        if blockchain is not None:
            for block in blockchain.chain:
                for transaction in block.transactions:
                    if not transaction.is_valid():
                        self.is_valid = False
                        return
                    from_address = transaction.from_address
                    to_address = transaction.to_address
                    amount = transaction.amount
                    if from_address is not None:
                        if from_address not in self.wallet_map or self.wallet_map[from_address] < amount:
                            self.is_valid = False
                            return
                        self.wallet_map[from_address] -= amount
                    if to_address not in self.wallet_map:
                        self.wallet_map[to_address] = 0
                    self.wallet_map[to_address] += amount

    def add(self,transaction):
        if not transaction.is_valid():
            return False
        from_address = transaction.from_address
        to_address = transaction.to_address
        amount = transaction.amount
        if from_address is not None:
            if from_address not in self.wallet_map or self.wallet_map[from_address] < amount:
                return False
            self.wallet_map[from_address] -= amount
        if to_address not in self.wallet_map:
            self.wallet_map[to_address] = 0
        self.wallet_map[to_address] += amount
        print("Add to my_state",to_address,self.wallet_map[to_address])
        return True