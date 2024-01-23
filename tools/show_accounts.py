import argparse
import requests
import sys
from pydantic import TypeAdapter
from blockchain.domain.block import Block

from blockchain.domain.blockchain import (
    Blockchain,
    accounts,
    integrate_inblock_transactions,
)

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=8080)
args = parser.parse_args()


res_chain = requests.get(f"http://{args.ip}:{str(args.port)}/chain")
if res_chain.status_code != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_jstr = res_chain.text
chain = TypeAdapter(list[Block]).validate_json(chain_jstr)
blockchain = Blockchain(outblock_transactions=[], chain=chain)

print(accounts(integrate_inblock_transactions(blockchain.chain)))
