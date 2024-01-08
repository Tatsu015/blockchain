from pydantic import BaseModel
from blockchain.block import Block
from blockchain.transaction import Transaction


class BlocksDTO(BaseModel):
    blocks: list[Block] = []


class TransactionsDTO(BaseModel):
    transactions: list[Transaction] = []
