from datetime import datetime
import pytest
from ecdsa import SECP256k1, BadSignatureError, VerifyingKey
import binascii
import json
import os
from datetime import datetime
from blockchain.block import Block
from blockchain.chain_repository_impl import ChainRepositoryImpl

from blockchain.transaction import new_transaction
from blockchain.blockchain import Blockchain, TransactionReuseError
from blockchain.transaction_repository_impl import TransactionRepositoryImpl


FROM_SELECT_KEY = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
TO_PUBLIC_KEY = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"


def test_restore_transactions():
    filepath = "test_transactions.json"

    transaction_repo1 = TransactionRepositoryImpl(filepath)
    t1 = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    t2 = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 10)
    transaction_repo1.save_transactions([t1, t2])

    transaction_repo2 = TransactionRepositoryImpl(filepath)
    transactions = transaction_repo2.load_transactios()

    assert t1 == transactions[0]
    assert t2 == transactions[1]

    os.remove(filepath)


def test_append_transactio():
    t = new_transaction(datetime.now(), FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    blockChain = Blockchain(outblock_transactions=[], chain=[])
    blockChain.add_transaction(t)

    with pytest.raises(TransactionReuseError) as e:
        blockChain.add_transaction(t)
    assert str(e.value) == "transaction already appended"


def test_restore_chain():
    filepath = "test_chain.json"
    chain_transactions1 = ChainRepositoryImpl(filepath)
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
    chain_transactions1.save_chain([b1, b2])

    chain_transactions2 = ChainRepositoryImpl(filepath)
    chain = chain_transactions2.load_chain()
    assert b1 == chain[0]
    assert b2 == chain[1]

    os.remove(filepath)


# def test_refresh_all_block_transactions():
#     blockChain = Blockchain()
#     t1 = new_transaction(
#         time=datetime.now(),
#         from_secret_key=FROM_SELECT_KEY,
#         to_public_key=TO_PUBLIC_KEY,
#         amount=11,
#     )
#     t2 = new_transaction(
#         time=datetime.now(),
#         from_secret_key=FROM_SELECT_KEY,
#         to_public_key=TO_PUBLIC_KEY,
#         amount=22,
#     )
#     t3 = new_transaction(
#         time=datetime.now(),
#         from_secret_key=FROM_SELECT_KEY,
#         to_public_key=TO_PUBLIC_KEY,
#         amount=33,
#     )

#     b1 = Block(
#         time=datetime.now(), transactions=[t1, t2], hash_value="testhash1", nonce=12345
#     )
#     b2 = Block(
#         time=datetime.now(), transactions=[t3], hash_value="testhash2", nonce=43234
#     )
#     blockChain.append_block(b1)
#     blockChain.append_block(b2)

#     blockChain.refresh_inblock_transactions()

#     assert t1 == blockChain.__inblock_transactions[0]
#     assert t2 == blockChain.__inblock_transactions[1]
#     assert t3 == blockChain.__inblock_transactions[2]
