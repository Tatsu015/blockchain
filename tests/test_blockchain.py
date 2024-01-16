from datetime import datetime
import pytest
from ecdsa import SECP256k1, BadSignatureError, VerifyingKey
import binascii
import json
import os
from datetime import datetime
from blockchain.block import Block

from blockchain.transaction import new_transaction
from blockchain.blockchain import FIRST_BLOCK, BlockChain, TransactionReuseError


FROM_SELECT_KEY = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
TO_PUBLIC_KEY = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"


def test_restore_transactions():
    filepath = "test_transactions.json"
    t1 = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    t2 = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 10)
    blockChain1 = BlockChain()
    blockChain1.append(t1)
    blockChain1.append(t2)
    blockChain1.save_transactions(filepath)

    blockChain2 = BlockChain()
    blockChain2.load_transactios(filepath)
    transactions = blockChain2.transactions_pool

    assert t1 == transactions[0]
    assert t2 == transactions[1]

    os.remove(filepath)


def test_append_transactio():
    t = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    blockChain = BlockChain()
    blockChain.append(t)

    with pytest.raises(TransactionReuseError) as e:
        blockChain.append(t)
    assert str(e.value) == "transaction already appended"


def test_restore_chain():
    filepath = "test_chain.json"
    blockChain = BlockChain()
    t1 = new_transaction(
        time=datetime.now(),
        from_secret_key=FROM_SELECT_KEY,
        to_public_key=TO_PUBLIC_KEY,
        amount=11,
    )
    t2 = new_transaction(
        time=datetime.now(),
        from_secret_key=FROM_SELECT_KEY,
        to_public_key=TO_PUBLIC_KEY,
        amount=22,
    )
    t3 = new_transaction(
        time=datetime.now(),
        from_secret_key=FROM_SELECT_KEY,
        to_public_key=TO_PUBLIC_KEY,
        amount=33,
    )

    b1 = Block(
        time=datetime.now(), transactions=[t1, t2], hash_value="testhash1", nonce=12345
    )
    b2 = Block(
        time=datetime.now(), transactions=[t3], hash_value="testhash2", nonce=43234
    )
    blockChain.chain.append(b1)
    blockChain.chain.append(b2)

    blockChain.save_chain(filepath)

    blockChain.load_chain(filepath)
    assert FIRST_BLOCK == blockChain.chain[0]
    assert b1 == blockChain.chain[1]
    assert b2 == blockChain.chain[2]

    os.remove(filepath)


def test_reset_all_block_transactions():
    blockChain = BlockChain()
    t1 = new_transaction(
        time=datetime.now(),
        from_secret_key=FROM_SELECT_KEY,
        to_public_key=TO_PUBLIC_KEY,
        amount=11,
    )
    t2 = new_transaction(
        time=datetime.now(),
        from_secret_key=FROM_SELECT_KEY,
        to_public_key=TO_PUBLIC_KEY,
        amount=22,
    )
    t3 = new_transaction(
        time=datetime.now(),
        from_secret_key=FROM_SELECT_KEY,
        to_public_key=TO_PUBLIC_KEY,
        amount=33,
    )

    b1 = Block(
        time=datetime.now(), transactions=[t1, t2], hash_value="testhash1", nonce=12345
    )
    b2 = Block(
        time=datetime.now(), transactions=[t3], hash_value="testhash2", nonce=43234
    )
    blockChain.chain.append(b1)
    blockChain.chain.append(b2)

    blockChain.refresh_all_block_transactions()

    assert t1 == blockChain.all_block_transactions[0]
    assert t2 == blockChain.all_block_transactions[1]
    assert t3 == blockChain.all_block_transactions[2]
