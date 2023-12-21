from pydantic import BaseModel
from blockchain.transaction import Transaction
from blockchain.blockchain_repository import TransactionRepository


class BlockChain(BaseModel):
    repository: TransactionRepository

    def add(self, transaction: Transaction) -> bool:
        try:
            transactions = self.repository.queryAll()
        except Exception as e:
            print(e)
            return
        if transaction in transactions:
            return False

        self.repository.add(transaction)
        return True

    def get_transactions(self) -> list[Transaction]:
        try:
            return self.repository.queryAll()
        except Exception as e:
            print(e)
            return []
