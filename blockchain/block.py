from datetime import datetime
from pydantic import BaseModel
from dataclasses import dataclass
from blockchain.transaction import Transaction


@dataclass(frozen=True)
class Block(BaseModel):
    time: datetime
    transactions: list[Transaction]
    hash: str
    nonce: int
