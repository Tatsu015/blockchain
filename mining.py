import requests
import sys
import json
from datetime import datetime
from pydantic import TypeAdapter
from blockchain.block import Block

from blockchain.blockchain import BlockChain
from blockchain.transaction import Transaction

# "51100f732f670c6223d4e341df8e5ab43a32da1c544d610493ca14b49de45488"
miner = "95029604df9f99e55392a443ea5dff802c41c9548bc182665c2f6b870cc18d0de4a9e438125aab1e63970d2eb4f3859323a6bb0e340fad03cb8b9dac4f52a3b0"
ip_addr = "127.0.0.1"
blockchain = BlockChain()

res_chain = requests.get("http://" + ip_addr + ":8080/chain")
if res_chain.status_code != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_json = res_chain.json()
print(res_chain.text)
blockchain.chain = TypeAdapter(list[Block]).validate_python(chain_json)

res_trans = requests.get("http://" + ip_addr + ":8080/transaction_pool")
if res_trans.status_code != 200:
    print(f"request error: {res_trans.status}")
    sys.exit()
trans_json = res_trans.json()
blockchain.transactions = TypeAdapter(list[Transaction]).validate_python(trans_json)

block = blockchain.new_block(now=datetime.now(), miner=miner)
blockchain.chain.append(block)

res = requests.post(
    "http://" + ip_addr + ":8080/chain", blockchain.chain.model_dump_json()
)

print(res.text)
