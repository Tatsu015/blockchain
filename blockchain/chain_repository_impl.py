import json
from pydantic.json import pydantic_encoder
from pydantic import TypeAdapter
from blockchain.block import Block
from blockchain.chain_repository import ChainRepository


class ChainRepositoryImpl(ChainRepository):
    def __init__(self, path: str) -> None:
        self.__path = path

    def load_chain(self):
        try:
            with open(self.__path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                chain = TypeAdapter(list[Block]).validate_json(json_data)
                return chain

        except FileNotFoundError as e:
            print(e)
            return []

    def save_chain(self, chain: list[Block]):
        with open(self.__path, "w", encoding="utf-8") as file:
            json_data = json.dumps(chain, default=pydantic_encoder)
            json.dump(json_data, file, default=str)
