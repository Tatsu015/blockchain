import requests
import sys
from datetime import datetime

from blockchain.transaction import new_transaction
from blockchain.blockchain import BlockChain, new_block
from fastapi.encoders import jsonable_encoder


from ecdsa import SigningKey, SECP256k1, VerifyingKey

# from_secret_key = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
# to_public_key = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"
# t = new_transaction(datetime.now(), from_secret_key, to_public_key, 10)

# data = jsonable_encoder(t)
# print("post data:", data)
# res = requests.post("http://127.0.0.1:8080/transaction_pool", json=data)

# sec_key = SigningKey.generate(curve=SECP256k1)
# print(sec_key.to_string().hex())
# pub = sec_key.verifying_key
# print(pub.to_string().hex())

# "51100f732f670c6223d4e341df8e5ab43a32da1c544d610493ca14b49de45488"
miner = "95029604df9f99e55392a443ea5dff802c41c9548bc182665c2f6b870cc18d0de4a9e438125aab1e63970d2eb4f3859323a6bb0e340fad03cb8b9dac4f52a3b0"
ip_addr = "127.0.0.1"
blockchain = BlockChain()

res_chain = requests("http://" + ip_addr + ":8080/transaction_pool")
if res_chain.status != 200:
    print(f"request error: {res_chain.status}")
    sys.exit()
chain_json = res_chain.json()
blockchain.chain = chain_json  # maybe NG

res_trans = requests("http://" + ip_addr + ":8080/transaction_pool")
if res_trans.status != 200:
    print(f"request error: {res_trans.status}")
    sys.exit()
trans_json = res_trans.json()
blockchain.transactions = trans_json  # maybe NG

block = blockchain.new_block(time=datetime.now(), miner=miner)
blockchain.chain.append(block)

res = requests.post(
    "http://" + ip_addr + ":8080/chain", blockchain.chain.model_dump_json()
)

print(res.text)
