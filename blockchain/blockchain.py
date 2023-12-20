from blockchain.transaction import Transaction
from pydantic import BaseModel


class BlockChain(BaseModel):
    def __init__(self):
        self.transactions: list[Transaction]

    def add(self, transaction: Transaction) -> bool:
        if transaction in self.transactions:
            return False
        self.transactions.append(transaction)
        return True
