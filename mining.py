import requests
import sys

import json

from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.block import Block

from blockchain.blockchain import Blockchain

from blockchain.transaction import Transaction
from blockchain.usecase import Usecase


miner_public_key = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"
ip_addr = "127.0.0.1"


def load_chain(ip_addr):
    res_chain = requests.get("http://" + ip_addr + ":8080/chain")
    if res_chain.status_code != 200:
        print(f"request error: {res_chain.status}")
        sys.exit()
    chain_jstr = res_chain.text
    chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
    return chain


def load_transactions(ip_addr):
    res_trans = requests.get("http://" + ip_addr + ":8080/transaction")
    if res_trans.status_code != 200:
        print(f"request error: {res_trans.status}")
        sys.exit()

    trans_jstr = res_trans.text
    transactions = []
    if trans_jstr != "":
        transactions = TypeAdapter(list[Transaction]).validate_json(trans_jstr)
    return transactions


chain = load_chain(ip_addr)
transactions = load_transactions(ip_addr)
blockchain = Blockchain()
usecase = Usecase()
message = usecase.mining(blockchain, miner_public_key, transactions, chain)

data = json.dumps(blockchain.chain, default=pydantic_encoder)

print(message)
res = requests.post("http://" + ip_addr + ":8080/chain", data=data)

print("response:", res.text)
