from datetime import datetime
import json
from pydantic import BaseModel
from blockchain.block import Block
from blockchain.transaction import Transaction
from typing import NewType

Chain = NewType("Chain", list[Block])


POW_DIFFICULTY = 10
REWARD_AMOUNT = 256


class TransactionReuseError(Exception):
    pass


class TransactionVerifyError(Exception):
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

    def reset_all_block_transactions(self):
        self.all_block_transactions = [b.transactions for b in self.chain]

    def verify(self, chain: Chain):
        all_transactions = []
        for i, now_block in enumerate(chain):
            if i == 0:
                if now_block != self.first_block:
                    raise TransactionVerifyError("first block maybe falsificated")

            prev_block = chain[i - 1]
            if now_block.hash != prev_block.hash():
                raise TransactionVerifyError("chain hash maybe falsificated")

            untime_now_block = now_block.to_untimed()
            if (format(int(untime_now_block.hash(), 16), "0256b"))[
                -POW_DIFFICULTY:
            ] != "0" * POW_DIFFICULTY:
                raise TransactionVerifyError(
                    "chain not satisfy mining success condition"
                )

            is_reward = False
            for transaction in now_block.transactions:
                if transaction.sender == "BlockChain":
                    if is_reward == True:
                        raise TransactionVerifyError("chain already contain reward")
                    else:
                        is_reward = True

                    if transaction.amount != REWARD_AMOUNT:
                        raise TransactionVerifyError("reward amount not correct")
                else:
                    transaction.verify()

                    if transaction not in all_transactions:
                        all_transactions.append(transaction)
                    else:
                        raise TransactionVerifyError("duplicate transaction")

    def replace(self, chain: Chain):
        pass
