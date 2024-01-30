import argparse
from datetime import datetime
import requests
import sys
import json
from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from blockchain.domain.block import Block, UntimedBlock
from blockchain.domain.blockchain import (
    POW_DIFFICULTY,
    REWARD_AMOUNT,
    Blockchain,
    has_minus_amount,
    integrate_inblock_transactions,
    verify,
)
from blockchain.domain.transaction import Transaction, new_reward_transaction


miner_public_key = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"


class MiningError(Exception):
    pass


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


def mining(
    miner_public_key: str,
    outblock_transactions: list[Transaction],
    chain: list[Block],
    reward_amount: int,
) -> Block:
    if len(chain) < 1:
        raise MiningError("empty chain not allowed")

    verify(chain)

    inblock_transactions = integrate_inblock_transactions(chain).copy()
    unique_transactions = _remove_reuse_transactions(
        outblock_transactions, inblock_transactions
    )

    copied_outblock_transactions = unique_transactions.copy()
    copied_inblock_transactions = integrate_inblock_transactions(chain).copy()
    for t in copied_outblock_transactions:
        copied_inblock_transactions.append(t)
        if has_minus_amount(copied_inblock_transactions):
            outblock_transactions.remove(t)
            copied_inblock_transactions.remove(t)

    block = _find_new_block(
        now=datetime.now(),
        miner=miner_public_key,
        outblock_transactions=outblock_transactions,
        chain=chain,
        reward_amount=reward_amount,
    )

    return block


def _remove_reuse_transactions(
    outblock_transactions: list[Transaction],
    copied_inblock_transactions: list[Transaction],
) -> list[Transaction]:
    copied_outblock_transactions = outblock_transactions.copy()
    for t in copied_outblock_transactions:
        if t not in copied_inblock_transactions:
            t.verify()
            copied_inblock_transactions.append(t)
        else:
            outblock_transactions.remove(t)

    return outblock_transactions.copy()


def _find_new_block(
    now: datetime,
    miner: str,
    outblock_transactions: list[Transaction],
    chain: list[Block],
    reward_amount: int,
) -> Block:
    reward_transaction = new_reward_transaction(
        time=now,
        receiver=miner,
        amount=reward_amount,
    )
    transactions = outblock_transactions.copy()
    transactions.append(reward_transaction)
    last_block = chain[-1]
    last_block_hash = last_block.hash()
    untimed_last_block = UntimedBlock(
        transactions=transactions, hash_value=last_block_hash, nonce=0
    )

    while untimed_last_block.is_wrong_hash(POW_DIFFICULTY):
        untimed_last_block.count_up_nonce()

    block = Block(
        time=datetime.now().isoformat(),
        transactions=untimed_last_block.transactions,
        hash_value=last_block_hash,
        nonce=untimed_last_block.nonce,
    )

    return block


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
