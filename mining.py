import requests
import sys

# import json
from datetime import datetime

# from pydantic import TypeAdapter
# from pydantic.json import pydantic_encoder
# from blockchain.block import Block

from blockchain.blockchain import BlockChain
from blockchain.dto import BlocksDTO, TransactionsDTO

# from blockchain.transaction import Transaction

miner = "95029604df9f99e55392a443ea5dff802c41c9548bc182665c2f6b870cc18d0de4a9e438125aab1e63970d2eb4f3859323a6bb0e340fad03cb8b9dac4f52a3b0"
ip_addr = "127.0.0.1"
blockchain = BlockChain()

res_chain = requests.get("http://" + ip_addr + ":8080/chain")
if res_chain.status_code != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_json = res_chain.json()
blockchain.chain = BlocksDTO.model_validate_json(json_data=chain_json)

res_trans = requests.get("http://" + ip_addr + ":8080/transaction_pool")
if res_trans.status_code != 200:
    print(f"request error: {res_trans.status}")
    sys.exit()
trans_json = res_trans.json()
if trans_json == []:
    blockchain.transactions = []
else:
    blockchain.transactions = TransactionsDTO.validate_json(
        trans_json
    )  # TypeAdapter(list[Transaction]).validate_json(trans_json)

block = blockchain.find_new_block(now=datetime.now(), miner=miner)
print(block)
blockchain.chain.append(block)

data = BlocksDTO(
    __root__=blockchain.chain
).model_dump_json()  # json.dumps(blockchain.chain, default=pydantic_encoder)
print("success mining!")
print("chain:", data)
res = requests.post("http://" + ip_addr + ":8080/chain", data=data)

print(res.text)
