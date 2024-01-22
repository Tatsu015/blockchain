import requests
import sys

import json
from datetime import datetime

from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.block import Block

from blockchain.blockchain import Blockchain, accounts, integrate_inblock_transactions


ip_addr = "127.0.0.1"

res_chain = requests.get("http://" + ip_addr + ":8080/chain")
if res_chain.status_code != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_jstr = res_chain.text
chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
blockchain = Blockchain(outblock_transactions=[], chain=chain)

print(accounts(integrate_inblock_transactions(blockchain.chain)))
