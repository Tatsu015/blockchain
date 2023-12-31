from datetime import datetime
from pydantic import BaseModel
import hashlib
from blockchain.transaction import Transaction


class UntimedBlock(BaseModel):
    transactions: list[Transaction]
    hash: str
    nonce: int

    def hash(self) -> str:
        h = hashlib.sha256(self.model_dump_json().encode("utf-8")).hexdigest()
        return h


class Block(BaseModel):
    time: datetime
    transactions: list[Transaction]
    hash: str
    nonce: int

    def hash(self) -> str:
        h = hashlib.sha256(self.model_dump_json().encode("utf-8")).hexdigest()
        return h

    def to_untimed(self) -> UntimedBlock:
        return UntimedBlock(
            transactions=self.transactions, hash=self.hash, nonce=self.nonce
        )
