from datetime import datetime
from pydantic import BaseModel
import hashlib
from blockchain.transaction import Transaction


class UntimedBlock(BaseModel):
    transactions: list[Transaction]
    hash: str
    nonce: int

    def hashed(self) -> str:
        encoded = self.model_dump_json().encode("utf-8")
        h = hashlib.sha256(encoded).hexdigest()
        return h

    def count_up_nonce(self):
        self.nonce += 1


class Block(BaseModel):
    time: datetime
    transactions: list[Transaction]
    hash: str
    nonce: int

    def hashed(self) -> str:
        h = hashlib.sha256(self.model_dump_json().encode("utf-8")).hexdigest()
        return h

    def to_untimed(self) -> UntimedBlock:
        return UntimedBlock(
            transactions=self.transactions, hash=self.hash, nonce=self.nonce
        )
