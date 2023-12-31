from datetime import datetime
import json
from pydantic import BaseModel, TypeAdapter
from pydantic.json import pydantic_encoder

from blockchain.block import Block, UntimedBlock
from blockchain.transaction import Transaction, new_transaction


POW_DIFFICULTY = 10
REWARD_AMOUNT = 256
MINING_SENDER_KEY = "BlockChainBlockChainBlockChain!!".encode("utf-8").hex()


class TransactionReuseError(Exception):
    pass


class TransactionVerifyError(Exception):
    pass


class BlockChain(BaseModel):
    transactions: list[Transaction] = []
    first_block: Block = Block(
        time=datetime.min, transactions=[], hash_value="SimplestBlockChain", nonce=0
    )
    chain: list[Block] = [first_block]
    all_block_transactions: list[Transaction] = []

    def load_transactios(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                self.transactions = TypeAdapter(list[Transaction]).validate_json(
                    json_data
                )

        except FileNotFoundError as e:
            print(e)

    def save_transactions(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json_data = json.dumps(self.transactions, default=pydantic_encoder)
            json.dump(json_data, file, default=str)

    def append(self, transaction: Transaction):
        if (transaction not in self.transactions) and (
            transaction not in self.all_block_transactions
        ):
            self.transactions.append(transaction)
        else:
            raise TransactionReuseError("transaction already appended")

    def load_chain(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
                self.chain = TypeAdapter(list[Block]).dump_python(json_data)

        except FileNotFoundError as e:
            print(e)

    def save_chain(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json_data = json.dumps(self.chain, default=pydantic_encoder)
            json.dump(json_data, file, default=str)

    def reset_all_block_transactions(self):
        self.all_block_transactions = [b.transactions for b in self.chain]

    def verify(self, chain: list[Block]):
        all_transactions = []
        for i, now_block in enumerate(chain):
            if i == 0:
                if now_block != self.first_block:
                    raise TransactionVerifyError("first block maybe falsificated")
            else:
                prev_block = chain[i - 1]
                if now_block.hash_value != prev_block.hash():
                    raise TransactionVerifyError("chain hash maybe falsificated")

                untime_now_block = now_block.to_untimed()
                if self.is_correct_hash(untime_now_block):
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

    def replace(self, chain: list[Block]):
        self.chain = chain
        self.reset_all_block_transactions()
        for transaction in self.all_block_transactions:
            if transaction in self.transactions:
                self.transactions.remove(transaction)

    def find_new_block(self, now: datetime, miner: str) -> Block:
        reward_transaction = new_transaction(
            time=now,
            from_secret_key=MINING_SENDER_KEY,
            to_public_key=miner,
            amount=REWARD_AMOUNT,
        )
        transactions = self.transactions.copy()
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
