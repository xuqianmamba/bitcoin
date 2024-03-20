import hashlib
def merkle_root(transactions):
    if len(transactions) == 0:
        return '0'
    
    # 如果交易数量不是偶数，将最后一个交易复制一份
    if len(transactions) % 2 != 0:
        transactions.append(transactions[-1])
        
    def combine(hash_list):
        if len(hash_list) == 1:
            return hash_list[0]
        new_hash_list = []
        for i in range(0, len(hash_list), 2):
            new_hash = hashlib.sha256((hash_list[i] + hash_list[i+1]).encode()).hexdigest()
            new_hash_list.append(new_hash)
        return combine(new_hash_list)
    
    transaction_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
    return combine(transaction_hashes)
