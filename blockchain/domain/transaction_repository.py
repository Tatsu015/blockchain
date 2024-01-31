from abc import ABC, abstractmethod

from blockchain.domain.transaction import Transaction


class TransactionRepository(ABC):
    @abstractmethod
    def load_transactios(self):
        pass

    @abstractmethod
    def save_transactions(self, transactions: list[Transaction]):
        pass
