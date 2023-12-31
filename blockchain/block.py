from datetime import datetime
from pydantic import BaseModel
from blockchain.transaction import Transaction


class Block(BaseModel):
    time: datetime
    transactions: list[Transaction]
    hash: str
    nonce: int
