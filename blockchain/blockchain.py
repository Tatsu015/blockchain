from datetime import datetime
import json
from pydantic import BaseModel
from blockchain.block import Block
from blockchain.transaction import Transaction
from typing import NewType

Chain = NewType("Chain", list[Block])


class TransactionReuseError(Exception):
    pass


class TransactionsMapper(BaseModel):
    transactions: list[Transaction]


class ChainMapper(BaseModel):
    chain: Chain


class BlockChain(BaseModel):
    transactions: list[Transaction] = []
    first_block: Block = Block(
        time=datetime.min, transactions=[], hash="SimplestBlockChain", nonce=0
    )
    chain: Chain = [first_block]
    all_block_transactions: list[Transaction] = []

    def load_transactios(self, path):
        try:
            with open(path, "r") as file:
                json_data = json.load(file)
                transactions_mapper = TransactionsMapper.model_validate_json(json_data)
                self.transactions = transactions_mapper.transactions

        except FileNotFoundError as e:
            print(e)

    def save_transactions(self, path):
        with open(path, "w") as file:
            transactions_mapper = TransactionsMapper(transactions=self.transactions)
            json_data = transactions_mapper.model_dump_json()
            json.dump(json_data, file, default=str)

    def append(self, transaction: Transaction):
        if (transaction in self.transactions) and (
            transaction in self.all_block_transactions
        ):
            raise TransactionReuseError("transaction already appended")

        self.transactions.append(transaction)

    def load_chain(self, path):
        try:
            with open(path, "r") as file:
                json_data = json.load(file)
                chain_mapper = ChainMapper.model_validate_json(json_data)
                self.chain = chain_mapper.chain

        except FileNotFoundError as e:
            print(e)

    def save_chain(self, path):
        with open(path, "w") as file:
            chain_mapper = ChainMapper(chain=self.chain)
            json_data = chain_mapper.model_dump_json()
            json.dump(json_data, file, default=str)

    def verify(self, chain: Chain):
        pass

    def replace(self, chain: Chain):
        pass
