import requests
import sys

import json
from datetime import datetime

from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.block import Block

from blockchain.blockchain import BlockChain, has_minus_amount

from blockchain.transaction import Transaction

miner_public_key = "68207f51dfde818044a41a116869e6ddccb6306375f94eff1ea9a69050458e7edd73a2c0e3bafb58b47d51b2f8123543f92ae2413a1f37abcf46ab379dcfc034"
ip_addr = "127.0.0.1"
blockchain = BlockChain()

res_chain = requests.get("http://" + ip_addr + ":8080/chain")
if res_chain.status_code != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_jstr = res_chain.text
blockchain.chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
blockchain.all_block_transactions()

res_trans = requests.get("http://" + ip_addr + ":8080/transaction_pool")
if res_trans.status_code != 200:
    print(f"request error: {res_trans.status}")
    sys.exit()

trans_jstr = res_trans.text
transactions = []
if trans_jstr != "":
    transactions = TypeAdapter(list[Transaction]).validate_json(trans_jstr)

copied_transactions = transactions.copy()
copied_all_block_transactions = blockchain.all_block_transactions.copy()
for t in copied_transactions:
    copied_all_block_transactions.append(t)
    if has_minus_amount(copied_all_block_transactions):
        transactions.remove(t)
        copied_all_block_transactions.remove(t)


blockchain.transactions_pool = transactions


block = blockchain.find_new_block(now=datetime.now(), miner=miner_public_key)
blockchain.chain.append(block)

data = json.dumps(blockchain.chain, default=pydantic_encoder)
print("success mining!")
print("chain:", data)
res = requests.post("http://" + ip_addr + ":8080/chain", data=data)

print("response:", res.text)
