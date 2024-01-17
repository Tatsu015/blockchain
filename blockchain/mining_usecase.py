from datetime import datetime
from blockchain.blockchain import Blockchain, find_new_block, has_minus_amount


def mining(miner_public_key, transactions, chain):
    blockchain = Blockchain()
    copied_transactions = transactions.copy()
    blockchain.chain = chain
    blockchain.refresh_inblock_transactions()
    copied_all_block_transactions = blockchain.inblock_transactions.copy()
    for t in copied_transactions:
        copied_all_block_transactions.append(t)
        if has_minus_amount(copied_all_block_transactions):
            transactions.remove(t)
            copied_all_block_transactions.remove(t)

    blockchain.outblock_transactions = transactions

    block = find_new_block(
        now=datetime.now(),
        miner=miner_public_key,
        outblock_transactions=blockchain.outblock_transactions,
        chain=blockchain.chain,
    )
    blockchain.chain.append(block)
    return blockchain
