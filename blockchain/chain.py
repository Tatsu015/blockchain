from pydantic import BaseModel
from blockchain.block import Block


class Chain(BaseModel):
    blocks: list[Block]
