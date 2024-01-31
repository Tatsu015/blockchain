from abc import ABC, abstractmethod

from blockchain.domain.block import Block


class ChainRepository(ABC):
    @abstractmethod
    def load_chain(self):
        pass

    @abstractmethod
    def save_chain(self, chain: list[Block]):
        pass
