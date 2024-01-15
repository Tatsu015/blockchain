import requests
import sys

import json
from datetime import datetime

from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.block import Block

from blockchain.blockchain import BlockChain, has_minus_amount

from blockchain.transaction import Transaction

miner_public_key = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"
ip_addr = "127.0.0.1"
blockchain = BlockChain()

res_chain = requests.get("http://" + ip_addr + ":8080/chain")
if res_chain.status_code != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_jstr = res_chain.text
blockchain.chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
blockchain.reset_all_block_transactions()

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
