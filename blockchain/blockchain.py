from datetime import datetime
import json
from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from itertools import chain

from blockchain.block import MINING_SENDER_KEY, Block, UntimedBlock
from blockchain.transaction import Transaction, new_transaction


POW_DIFFICULTY = 10
REWARD_AMOUNT = 256
FIRST_BLOCK = Block(
    time=datetime.min, transactions=[], hash_value="SimplestBlockChain", nonce=0
)


class TransactionReuseError(Exception):
    pass


class TransactionVerifyError(Exception):
    pass


class Blockchain:
    def __init__(
        self, outblock_transactions: list[Transaction], chain: list[Block]
    ) -> None:
        self._outblock_transactions: list[Transaction] = outblock_transactions
        self._chain: list[Block] = chain
        self._inblock_transactions: list[Transaction] = []

        if self._chain == []:
            self._chain = [FIRST_BLOCK]

    @property
    def outblock_transactions(self) -> list[Transaction]:
        return self._outblock_transactions

    @property
    def chain(self) -> list[Block]:
        return self._chain

    @property
    def inblock_transactions(self) -> list[Transaction]:
        return self._inblock_transactions

    @outblock_transactions.setter
    def outblock_transactions(self, value):
        self._outblock_transactions = value

    @chain.setter
    def chain(self, value):
        self._chain = value

    def load_transactios(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                self._outblock_transactions = TypeAdapter(
                    list[Transaction]
                ).validate_json(json_data)

        except FileNotFoundError as e:
            print(e)

    def save_transactions(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json_data = json.dumps(
                self._outblock_transactions, default=pydantic_encoder
            )
            json.dump(json_data, file, default=str)

    def add_transaction(self, transaction: Transaction):
        if (transaction not in self._outblock_transactions) and (
            transaction not in self._inblock_transactions
        ):
            self._outblock_transactions.append(transaction)
        else:
            raise TransactionReuseError("transaction already appended")

    def load_chain(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                self._chain = TypeAdapter(list[Block]).validate_json(json_data)

        except FileNotFoundError as e:
            print(e)

    def save_chain(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json_data = json.dumps(self._chain, default=pydantic_encoder)
            json.dump(json_data, file, default=str)

    def add_block(self, block: Block):
        self._chain.append(block)

    def refresh_inblock_transactions(self):
        block_transactions = [b.transactions for b in self._chain]
        all_transactions = list(chain.from_iterable(block_transactions))
        self._inblock_transactions = all_transactions

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
                if untime_now_block.is_wrong_hash(POW_DIFFICULTY):
                    raise TransactionVerifyError(
                        "chain not satisfy mining success condition"
                    )

                if now_block.has_many_rewards():
                    raise TransactionVerifyError("chain already contain reward")

                if now_block.has_bad_reward(REWARD_AMOUNT):
                    raise TransactionVerifyError("reward amount not correct")

                if now_block.contain(all_transactions):
                    raise TransactionVerifyError("duplicate transaction")

                now_block.verify()

                all_transactions.extend(now_block.transactions)

        if has_minus_amount(transactions=all_transactions):
            raise TransactionVerifyError("minus amount exist")

    def replace(self, chain: list[Block]):
        self._chain = chain
        self.refresh_inblock_transactions()
        for transaction in self._inblock_transactions:
            if transaction in self._outblock_transactions:
                self._outblock_transactions.remove(transaction)


def find_new_block(
    now: datetime,
    miner: str,
    outblock_transactions: list[Transaction],
    chain: list[Block],
) -> Block:
    reward_transaction = Transaction(
        time=now,
        sender=MINING_SENDER_KEY,
        receiver=miner,
        amount=REWARD_AMOUNT,
        signature="none",
    )
    transactions = outblock_transactions.copy()
    transactions.append(reward_transaction)
    last_block = chain[-1]
    last_block_hash = last_block.hash()
    untimed_last_block = UntimedBlock(
        transactions=transactions, hash_value=last_block_hash, nonce=0
    )

    while untimed_last_block.is_wrong_hash(POW_DIFFICULTY):
        untimed_last_block.count_up_nonce()

    block = Block(
        time=datetime.now().isoformat(),
        transactions=untimed_last_block.transactions,
        hash_value=last_block_hash,
        nonce=untimed_last_block.nonce,
    )

    return block


def accounts(transactions: list[Transaction]) -> dict[str, int]:
    accounts: dict[str, int] = {}
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

    return min_amount < 0
