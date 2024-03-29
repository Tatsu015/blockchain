from blockchain.domain.block import Block
from blockchain.domain.blockchain import Blockchain, verify
from blockchain.domain.chain_repository import ChainRepository
from blockchain.domain.transaction import Transaction
from blockchain.domain.transaction_repository import TransactionRepository
from blockchain.infrastructure.syncer_impl import SyncerImpl


class Usecase:
    def __init__(
        self,
        blockchain: Blockchain,
        transaction_repository: TransactionRepository,
        chain_repository: ChainRepository,
        syncer: SyncerImpl,
    ) -> None:
        self._blockchain = blockchain
        self._transaction_repository = transaction_repository
        self._chain_repository = chain_repository
        self._syncer = syncer
        pass

    def get_outblock_transaction(self) -> list[Transaction]:
        return self._blockchain.outblock_transactions

    def add_transaction(self, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        self._blockchain.add_transaction(transaction)
        self._transaction_repository.save_transactions(
            self._blockchain.outblock_transactions
        )
        self._syncer.bloadcast(transaction)
        return "Transaction is posted"

    def add_transaction_without_bloadcast(self, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        self._blockchain.add_transaction(transaction)
        self._transaction_repository.save_transactions(
            self._blockchain.outblock_transactions
        )
        return "Transaction is received"

    def get_chain(self) -> list[Block]:
        return self._blockchain.chain

    def update_chain(self, chain: list[Block]) -> str:
        if len(chain) <= len(self._blockchain.chain):
            return "Received chain is ignored"
        try:
            pow_difficulty = verify(chain)
            self._blockchain.pow_difficulty = pow_difficulty
            self._blockchain.replace(chain)
            self._chain_repository.save_chain(self._blockchain.chain)
            self._transaction_repository.save_transactions(
                self._blockchain.outblock_transactions
            )
            return "chain is posted"

        except Exception as e:
            print(e)
            return str(e)
