import requests
import sys

import json
from datetime import datetime

from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.block import Block

from blockchain.blockchain import BlockChain, accounts, has_minus_amount

from blockchain.transaction import Transaction

ip_addr = "127.0.0.1"
blockchain = BlockChain()

res_chain = requests.get("http://" + ip_addr + ":8080/chain")
if res_chain.status_code != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_jstr = res_chain.text
blockchain.chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
blockchain.reset_all_block_transactions()

print(accounts(blockchain.all_block_transactions))
