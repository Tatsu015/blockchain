from datetime import datetime
from itertools import chain as iter_chain

from blockchain.domain.block import MINING_SENDER_KEY, Block
from blockchain.domain.transaction import Transaction


POW_DIFFICULTY_ORIGIN = 18
POW_CHAINGE_BLOCK_NUM = 10
POW_TARGET_SEC = 10
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
        self._pow_difficulty = POW_DIFFICULTY_ORIGIN

        if self._chain == []:
            self._chain = [FIRST_BLOCK]

        self.replace(self._chain)

    @property
    def outblock_transactions(self) -> list[Transaction]:
        return self._outblock_transactions

    @property
    def chain(self) -> list[Block]:
        return self._chain

    @property
    def inblock_transactions(self) -> list[Transaction]:
        return self._inblock_transactions

    @property
    def pow_difficulty(self) -> int:
        return self._pow_difficulty

    @outblock_transactions.setter
    def outblock_transactions(self, value):
        self._outblock_transactions = value

    @chain.setter
    def chain(self, value):
        self._chain = value

    @pow_difficulty.setter
    def pow_difficulty(self, value):
        self._pow_difficulty = value

    def add_transaction(self, transaction: Transaction):
        if (transaction not in self._outblock_transactions) and (
            transaction not in self._inblock_transactions
        ):
            self._outblock_transactions.append(transaction)
        else:
            raise TransactionReuseError("transaction already appended")

    def add_block(self, block: Block):
        self._chain.append(block)

    def replace(self, chain: list[Block]):
        self._chain = chain
        self._inblock_transactions = integrate_inblock_transactions(self.chain)
        for transaction in self._inblock_transactions:
            if transaction in self._outblock_transactions:
                self._outblock_transactions.remove(transaction)


def get_pow_difficulty(blocks: list[Block], current_pow_difficulty: int) -> int:
    ix = len(blocks) - 1
    if ix - 1 % POW_CHAINGE_BLOCK_NUM == 0 and 1 < ix:
        all_time = 0
        for i in range(POW_CHAINGE_BLOCK_NUM):
            all_time += (blocks[ix - i].time - blocks[ix - i - 1].time).total_seconds()

        if all_time / POW_CHAINGE_BLOCK_NUM < POW_TARGET_SEC / 2:
            current_pow_difficulty += 1
        if (
            1 < current_pow_difficulty
            and POW_TARGET_SEC * 2 < all_time / POW_CHAINGE_BLOCK_NUM
        ):
            current_pow_difficulty -= 1
    return current_pow_difficulty


def verify(chain: list[Block]) -> int:
    all_transactions = []
    current_pow_difficulty = POW_DIFFICULTY_ORIGIN
    for i, now_block in enumerate(chain):
        if i == 0:
            if now_block != FIRST_BLOCK:
                raise TransactionVerifyError("first block maybe falsificated")
        else:
            prev_block = chain[i - 1]
            if now_block.hash_value != prev_block.hash():
                raise TransactionVerifyError("chain hash maybe falsificated")

            untime_now_block = now_block.to_untimed()
            current_pow_difficulty = get_pow_difficulty(
                chain[:i], current_pow_difficulty
            )
            if untime_now_block.is_wrong_hash(current_pow_difficulty):
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
    return current_pow_difficulty


def integrate_inblock_transactions(chain: list[Block]) -> list[Transaction]:
    block_transactions = [b.transactions for b in chain]
    all_transactions = list(iter_chain.from_iterable(block_transactions))
    return all_transactions


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
