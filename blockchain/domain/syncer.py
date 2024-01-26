from abc import ABC, abstractmethod

from blockchain.domain.transaction import Transaction


class Syncer(ABC):
    @abstractmethod
    def bloadcast(self, transaction: Transaction):
        pass
