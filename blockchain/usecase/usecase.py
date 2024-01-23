from blockchain.domain.block import Block
from blockchain.domain.blockchain import Blockchain
from blockchain.domain.chain_repository import ChainRepository
from blockchain.domain.transaction import Transaction
from blockchain.domain.transaction_repository import TransactionRepository


class Usecase:
    def __init__(
        self,
        blockchain: Blockchain,
        transaction_repository: TransactionRepository,
        chain_repository: ChainRepository,
    ) -> None:
        self._blockchain = blockchain
        self._transaction_repository = transaction_repository
        self._chain_repository = chain_repository
        pass

    def get_outblock_transaction(self) -> list[Transaction]:
        return self._blockchain.outblock_transactions

    def add_transaction(self, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        self._blockchain.add_transaction(transaction)
        self._transaction_repository.save_transactions("transactions.json")
        return "Transaction is posted"

    def get_chain(self) -> list[Block]:
        return self._blockchain.chain

    def update_chain(self, chain: list[Block]) -> str:
        if len(chain) <= len(self._blockchain.chain):
            return "Received chain is ignored"
        try:
            self._blockchain.verify(chain)
            self._blockchain.replace(chain)
            self._chain_repository.save_chain("chain.json")
            self._transaction_repository.save_transactions("transactions.json")
            return "chain is posted"

        except Exception as e:
            print(e)
            return str(e)
