from abc import ABC, abstractmethod


class TransactionRepository(ABC):
    @abstractmethod
    def load_transactios(self):
        pass

    @abstractmethod
    def save_transactions(self):
        pass
