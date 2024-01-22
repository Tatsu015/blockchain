from blockchain.block import Block
from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction


class Usecase:
    def __init__(self, blockchain: Blockchain) -> None:
        self._blockchain = blockchain
        pass

    def get_outblock_transaction(self) -> list[Transaction]:
        return self._blockchain.outblock_transactions

    def add_transaction(self, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        self._blockchain.add_transaction(transaction)
        self._blockchain.save_transactions("transactions.json")
        return "Transaction is posted"

    def get_chain(self) -> list[Block]:
        return self._blockchain.chain

    def update_chain(self, chain: list[Block]) -> str:
        if len(chain) <= len(self._blockchain.chain):
            return "Received chain is ignored"
        try:
            self._blockchain.verify(chain)
            self._blockchain.replace(chain)
            self._blockchain.save_chain("chain.json")
            self._blockchain.save_transactions("transactions.json")
            return "chain is posted"

        except Exception as e:
            print(e)
            return str(e)
