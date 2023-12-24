from datetime import datetime
import pytest
from ecdsa import SECP256k1, BadSignatureError, VerifyingKey
import binascii
import json
import os
from datetime import datetime

from blockchain.transaction import Transaction, new_transaction
from blockchain.blockchain import BlockChain


FROM_SELECT_KEY = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
TO_PUBLIC_KEY = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"


def test_restore_transactions():
    filepath = "test_signed_transaction.json"
    t1 = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    t2 = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 10)
    blockChain1 = BlockChain()
    blockChain1.append(t1)
    blockChain1.append(t2)
    blockChain1.save(filepath)

    blockChain2 = BlockChain()
    blockChain2.load(filepath)
    transactions = blockChain2.get_transactions()

    assert t1 == transactions[0]
    assert t2 == transactions[1]

    os.remove(filepath)


def test_add_same_transaction_not_accept():
    t = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    blockChain = BlockChain()

    assert True == blockChain.append(t)
    assert False == blockChain.append(t)
    ts = blockChain.get_transactions()
    t1 = ts[0]

    # about t1
    from_pub_key1 = VerifyingKey.from_string(
        binascii.unhexlify(t1.sender), curve=SECP256k1
    )
    signature1 = binascii.unhexlify(t1.signature)
    unsigned_json1 = t1.to_unsigned().model_dump_json()
    from_pub_key1.verify(signature1, unsigned_json1.encode("utf-8"))

    assert True is True