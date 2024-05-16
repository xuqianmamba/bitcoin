import hashlib

def merkle_root(transactions):
    if len(transactions) == 0:
        return '0'
    
    def combine(hash_list):
        if len(hash_list) == 1:
            return hash_list[0]
        if len(hash_list) % 2 != 0:
            hash_list.append(hash_list[-1])  # 确保每次递归调用时，列表长度为偶数
        new_hash_list = []
        for i in range(0, len(hash_list), 2):
            new_hash = hashlib.sha256((hash_list[i] + hash_list[i+1]).encode()).hexdigest()
            new_hash_list.append(new_hash)
        return combine(new_hash_list)
    
    transaction_hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
    return combine(transaction_hashes)