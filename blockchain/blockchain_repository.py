import json
from blockchain.transaction import Transaction
from blockchain.blockchain import BlockChain
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class Transactions(BaseModel):
    transactions: list[Transaction]


class TransactionRepository:
    def __init__(self, path):
        self.path = path

        try:
            with open(self.path, "r") as file:
                json_data = json.load(file)
                self.block_chain = BlockChain.model_validate_json(json_data)
                return self.block_chain

        except FileNotFoundError as e:
            print(e)

    def queryAll(self) -> list[Transaction]:
        try:
            with open(self.path, "r") as file:
                json_data = json.load(file)
                transactions = Transactions.model_validate_json(json_data)
                return transactions

        except (FileNotFoundError, ValueError) as e:
            print(e)

    # def query(self, id: int) -> Transaction:
    #     try:
    #         transactions = self.queryAll()
    #         transaction = next((x for x in transactions if x.id == id), None)
    #         return transaction

    #     except (FileNotFoundError, ValueError) as e:
    #         print(e)

    def add(self, transaction: Transaction):
        try:
            with open(self.path, "r") as file:
                json_data = json.load(file)
                transactions = Transactions.model_validate_json(json_data)
                transactions.transactions.append(transaction)

            with open(self.path, "w") as file:
                json_data = transactions.model_dump_json()
                json.dump(json_data, file, default=str)

        except FileNotFoundError as e:
            print(e)
