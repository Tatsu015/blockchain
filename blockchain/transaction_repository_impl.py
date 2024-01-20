import json
from pydantic.json import pydantic_encoder
from pydantic import TypeAdapter
from blockchain.transaction import Transaction
from blockchain.transaction_repository import TransactionRepository


class TransactionRepositoryImpl(TransactionRepository):
    def __init__(self, path: str) -> None:
        self.__path = path

    def load_transactios(self):
        try:
            with open(self.__path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                transactions = TypeAdapter(list[Transaction]).validate_json(json_data)

                return transactions

        except FileNotFoundError as e:
            print(e)
            return []

    def save_transactions(self, transactions: list[Transaction]):
        with open(self.__path, "w", encoding="utf-8") as file:
            json_data = json.dumps(transactions, default=pydantic_encoder)
            json.dump(json_data, file, default=str)
