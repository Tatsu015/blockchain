import argparse
import requests
import sys
import json
from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.domain.block import Block
from blockchain.domain.block import MINING_SENDER_KEY, Block, UntimedBlock
from blockchain.domain.blockchain import (
    REWARD_AMOUNT,
    Blockchain,
)
from blockchain.domain.transaction import Transaction
from blockchain.lib.mining import mining


miner_public_key = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"


def fetch_longest_chain(hosts: list[str]) -> list[Block]:
    chains = [fetch_chain(h) for h in hosts]
    chain = max(chains, key=lambda obj: len(obj))
    return chain


def fetch_chain(host: str):
    url = f"http://{host}/chain"
    try:
        res_chain = requests.get(url)
        if res_chain.status_code != 200:
            print(f"request error: {res_chain.status}")
            return []
    except:
        return []

    chain_jstr = res_chain.text
    chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
    return chain


def fetch_longest_outblock_transactions(hosts: list[str]) -> list[Block]:
    transactions_list = [fetch_outblock_transactions(h) for h in hosts]
    transactions = max(transactions_list, key=lambda obj: len(obj))
    return transactions


def fetch_outblock_transactions(host: str):
    url = f"http://{host}/transaction"
    try:
        res_trans = requests.get(url)
        if res_trans.status_code != 200:
            print(f"request error: {res_trans.status}")
            return []
    except:
        return []

    trans_jstr = res_trans.text
    transactions = []
    if trans_jstr != "":
        transactions = TypeAdapter(list[Transaction]).validate_json(trans_jstr)
    return transactions


parser = argparse.ArgumentParser()
parser.add_argument(
    "--hosts",
    type=str,
    default="127.0.0.1:8080,127.0.0.1:8081,127.0.0.1:8082,127.0.0.1:8083",
)
args = parser.parse_args()
hosts = args.hosts.split(",")
chain = fetch_longest_chain(hosts)
outblock_transactions = fetch_longest_outblock_transactions(hosts)
blockchain = Blockchain(outblock_transactions, chain)

new_block = mining(miner_public_key, outblock_transactions, chain, REWARD_AMOUNT)
blockchain.add_block(new_block)
data = json.dumps(blockchain.chain, default=pydantic_encoder)

print("success to mining")
for host in hosts:
    url = f"http://{host}/chain"
    res = requests.post(url, data=data)

    print(f"response {host}:", res.text)
