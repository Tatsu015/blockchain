import json
from pydantic import BaseModel
from blockchain.transaction import Transaction


class BlockChain(BaseModel):
    transactions: list[Transaction] = []

    def load(self, path):
        try:
            with open(path, "r") as file:
                json_data = json.load(file)
                self.transactions = BlockChain.model_validate_json(
                    json_data
                ).transactions

        except FileNotFoundError as e:
            print(e)

    def save(self, path):
        with open(path, "w") as file:
            json_data = self.model_dump_json()
            json.dump(json_data, file, default=str)

    def append(self, transaction: Transaction) -> bool:
        if transaction in self.transactions:
            return False

        self.transactions.append(transaction)
        return True

    def get_transactions(self) -> list[Transaction]:
        return self.transactions
