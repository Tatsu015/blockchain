from datetime import datetime
import json
from pydantic import BaseModel, TypeAdapter
from pydantic.json import pydantic_encoder
from itertools import chain

from blockchain.block import Block, UntimedBlock
from blockchain.transaction import Transaction, new_transaction


POW_DIFFICULTY = 10
REWARD_AMOUNT = 256
MINING_SENDER_KEY = "BlockChain"
FIRST_BLOCK = Block(
    time=datetime.min, transactions=[], hash_value="SimplestBlockChain", nonce=0
)


class TransactionReuseError(Exception):
    pass


class TransactionVerifyError(Exception):
    pass


class BlockChain(BaseModel):
    transactions_pool: list[Transaction] = []
    chain: list[Block] = [FIRST_BLOCK]
    all_block_transactions: list[Transaction] = []

    def load_transactios(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                self.transactions_pool = TypeAdapter(list[Transaction]).validate_json(
                    json_data
                )

        except FileNotFoundError as e:
            print(e)

    def save_transactions(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json_data = json.dumps(self.transactions_pool, default=pydantic_encoder)
            json.dump(json_data, file, default=str)

    def append(self, transaction: Transaction):
        if (transaction not in self.transactions_pool) and (
            transaction not in self.all_block_transactions
        ):
            self.transactions_pool.append(transaction)
        else:
            raise TransactionReuseError("transaction already appended")

    def load_chain(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                self.chain = TypeAdapter(list[Block]).validate_json(json_data)

        except FileNotFoundError as e:
            print(e)

    def save_chain(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json_data = json.dumps(self.chain, default=pydantic_encoder)
            json.dump(json_data, file, default=str)

    def reset_all_block_transactions(self):
        block_transactions = [b.transactions for b in self.chain]
        all_transactions = list(chain.from_iterable(block_transactions))
        self.all_block_transactions = all_transactions

    def verify(self, chain: list[Block]):
        all_transactions = []
        for i, now_block in enumerate(chain):
            if i == 0:
                if now_block != FIRST_BLOCK:
                    raise TransactionVerifyError("first block maybe falsificated")
            else:
                prev_block = chain[i - 1]
                if now_block.hash_value != prev_block.hash():
                    raise TransactionVerifyError("chain hash maybe falsificated")

                untime_now_block = now_block.to_untimed()
                if not self.is_correct_hash(untime_now_block):
                    raise TransactionVerifyError(
                        "chain not satisfy mining success condition"
                    )

                is_reward = False
                for transaction in now_block.transactions:
                    if transaction.sender == MINING_SENDER_KEY:
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

        if has_minus_amount(transactions=all_transactions):
            raise TransactionVerifyError("has minus amount")

    def replace(self, chain: list[Block]):
        self.chain = chain
        self.reset_all_block_transactions()
        for transaction in self.all_block_transactions:
            if transaction in self.transactions_pool:
                self.transactions_pool.remove(transaction)

    def find_new_block(self, now: datetime, miner: str) -> Block:
        reward_transaction = Transaction(
            time=now,
            sender=MINING_SENDER_KEY,
            receiver=miner,
            amount=REWARD_AMOUNT,
            signature="none",
        )
        transactions = self.transactions_pool.copy()
        transactions.append(reward_transaction)
        last_block = self.chain[-1]
        last_block_hash = last_block.hash()
        untimed_last_block = UntimedBlock(
            transactions=transactions, hash_value=last_block_hash, nonce=0
        )

        while not self.is_correct_hash(untimed_block=untimed_last_block):
            untimed_last_block.count_up_nonce()

        block = Block(
            time=datetime.now().isoformat(),
            transactions=untimed_last_block.transactions,
            hash_value=last_block_hash,
            nonce=untimed_last_block.nonce,
        )

        return block

    def is_correct_hash(self, untimed_block: UntimedBlock) -> bool:
        hex_hash = format(int(untimed_block.hash(), 16), "0256b")
        hash_end = hex_hash[-POW_DIFFICULTY:]
        return hash_end == "0" * POW_DIFFICULTY


def accounts(transactions: list[Transaction]) -> object:
    accounts = {}
    copied_transactions = transactions.copy()

    for transaction in copied_transactions:
        if transaction.sender != MINING_SENDER_KEY:
            if transaction.sender not in accounts:
                accounts[transaction.sender] = int(0)
            accounts[transaction.sender] -= transaction.amount
        if transaction.receiver not in accounts:
            accounts[transaction.receiver] = int(0)
        accounts[transaction.receiver] += transaction.amount

    return accounts


def has_minus_amount(transactions: list[Transaction]) -> bool:
    if transactions == []:
        return False
    min_amount = min(accounts(transactions).values())
    if min_amount < 0:
        return False
    return True
