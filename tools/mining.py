import argparse
import requests
import sys
import json
from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.domain.block import Block
from blockchain.domain.blockchain import (
    REWARD_AMOUNT,
    Blockchain,
    integrate_inblock_transactions,
    mining,
    verify,
)
from blockchain.domain.transaction import Transaction


miner_public_key = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"


def fetch_chain(ip_addr: str, port: int):
    res_chain = requests.get(f"http://{ip_addr}:{str(port)}/chain")
    if res_chain.status_code != 200:
        print(f"request error: {res_chain.status}")
        sys.exit()
    chain_jstr = res_chain.text
    chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
    return chain


def fetch_outblock_transactions(ip_addr: str, port: int):
    res_trans = requests.get(f"http://{ip_addr}:{str(port)}/transaction")
    if res_trans.status_code != 200:
        print(f"request error: {res_trans.status}")
        sys.exit()

    trans_jstr = res_trans.text
    transactions = []
    if trans_jstr != "":
        transactions = TypeAdapter(list[Transaction]).validate_json(trans_jstr)
    return transactions


parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=8080)
args = parser.parse_args()

chain = fetch_chain(args.ip, args.port)
outblock_transactions = fetch_outblock_transactions(args.ip, args.port)
blockchain = Blockchain(outblock_transactions, chain)

new_block = mining(miner_public_key, outblock_transactions, chain, REWARD_AMOUNT)
blockchain.add_block(new_block)
data = json.dumps(blockchain.chain, default=pydantic_encoder)

print("success to mining")
res = requests.post(f"http://{args.ip}:{str(args.port)}/chain", data=data)

print("response:", res.text)
