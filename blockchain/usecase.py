from datetime import datetime
from blockchain.block import Block
from blockchain.blockchain import Blockchain, find_new_block, has_minus_amount
from blockchain.transaction import Transaction


class Usecase:
    def __init__(self) -> None:
        pass

    def get_outblock_transaction(self, blockchain: Blockchain) -> list[Transaction]:
        return blockchain.outblock_transactions

    def add_transaction(self, blockchain: Blockchain, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        blockchain.append(transaction)
        blockchain.save_transactions("transactions.json")
        return "Transaction is posted"

    def get_chain(self, blockchain: Blockchain) -> list[Block]:
        return blockchain.chain

    def add_chain(self, blockchain: Blockchain, chain: list[Block]) -> str:
        if len(chain) <= len(blockchain.chain):
            return "Received chain is ignored"
        try:
            blockchain.verify(chain)
            blockchain.replace(chain)
            blockchain.save_chain("chain.json")
            blockchain.save_transactions("transactions.json")
            return "chain is posted"

        except Exception as e:
            print(e)
            return str(e)

    def mining(self, miner_public_key, transactions, chain):
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
