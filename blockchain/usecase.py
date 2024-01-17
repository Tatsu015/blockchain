from blockchain.block import Block
from blockchain.blockchain import Blockchain
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
