from blockchain.transaction import Transaction
import json
from pydantic import BaseModel


class Transactions(BaseModel):
    transactions: list[Transaction]


class TransactionRepository:
    def __init__(self, path):
        self.path = path
        self.transactions: list[Transaction] = []

    def load(self) -> list[Transaction]:
        try:
            with open(self.path, "r") as file:
                json_data = json.load(file)
                self.transactions = Transactions.model_validate_json(
                    json_data
                ).transactions
                return self.transactions

        except FileNotFoundError as e:
            print(e)

    def save(self):
        with open(self.path, "w") as file:
            ts = Transactions(transactions=self.transactions)
            json_data = ts.model_dump_json()
            json.dump(json_data, file, default=str)

        return

    def add(self, transaction: Transaction):
        self.transactions.append(transaction)
