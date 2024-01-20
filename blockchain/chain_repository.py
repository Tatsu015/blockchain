from abc import ABC, abstractmethod


class ChainRepository(ABC):
    @abstractmethod
    def load_chain(self):
        pass

    @abstractmethod
    def save_chain(self):
        pass
