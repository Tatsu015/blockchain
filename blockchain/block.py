from datetime import datetime
from pydantic import BaseModel
import hashlib
from blockchain.transaction import Transaction

MINING_SENDER_KEY = "Blockchain"


class UntimedBlock(BaseModel):
    transactions: list[Transaction]
    hash_value: str
    nonce: int

    def hash(self) -> str:
        encoded = self.model_dump_json().encode("utf-8")
        h = hashlib.sha256(encoded).hexdigest()
        return h

    def count_up_nonce(self):
        self.nonce += 1

    def is_wrong_hash(self, pow_difficulty: int) -> bool:
        hex_hash = format(int(self.hash(), 16), "0256b")
        hash_end = hex_hash[-pow_difficulty:]
        return hash_end != "0" * pow_difficulty


class Block(BaseModel):
    time: datetime
    transactions: list[Transaction]
    hash_value: str
    nonce: int

    def hash(self) -> str:
        h = hashlib.sha256(self.model_dump_json().encode("utf-8")).hexdigest()
        return h

    def to_untimed(self) -> UntimedBlock:
        return UntimedBlock(
            transactions=self.transactions, hash_value=self.hash_value, nonce=self.nonce
        )

    def has_many_rewards(self) -> bool:
        is_reward = False
        for transaction in self.transactions:
            if transaction.sender == MINING_SENDER_KEY:
                if is_reward == True:
                    return True
                else:
                    is_reward = True

        return False

    def has_bad_reward(self, reward_amount) -> bool:
        for transaction in self.transactions:
            if transaction.sender == MINING_SENDER_KEY:
                if transaction.amount != reward_amount:
                    return True
        return False

    def contain(self, transactions: list[Transaction]) -> bool:
        return any(item in transactions for item in self.transactions)

    def verify(self):
        for transaction in self.transactions:
            # mining transaction not need to verify
            # because reward transaction parameter set by hand and not satisfy verification
            if transaction.sender != MINING_SENDER_KEY:
                transaction.verify()
