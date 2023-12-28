import json
from pydantic import BaseModel
from blockchain.chain import Chain
from blockchain.transaction import Transaction


class TransactionReuseError(Exception):
    pass


class Transactions(BaseModel):
    transactions: list[Transaction]


class BlockChain(BaseModel):
    transactions: list[Transaction] = []
    chain: Chain

    def load(self, path):
        try:
            with open(path, "r") as file:
                json_data = json.load(file)
                transactions = Transactions.model_validate_json(json_data)
                self.transactions = transactions.transactions

        except FileNotFoundError as e:
            print(e)

    def save(self, path):
        with open(path, "w") as file:
            transactions = Transactions(transactions=self.transactions)
            json_data = transactions.model_dump_json()
            json.dump(json_data, file, default=str)

    def append(self, transaction: Transaction):
        if transaction in self.transactions:
            raise TransactionReuseError("transaction already appended")

        self.transactions.append(transaction)

    def get_transactions(self) -> list[Transaction]:
        return self.transactions

    def get_chain(self) -> Chain:
        return self.chain

    def verify(self, chain: Chain):
        pass

    def replace(self, chain: Chain):
        pass
