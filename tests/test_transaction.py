from datetime import datetime
import pytest
from ecdsa import SECP256k1, BadSignatureError, VerifyingKey
import binascii
import json
import os
from datetime import datetime

from blockchain.transaction import Transaction, new_transaction
from blockchain.blockchain import BlockChain


TRANSACTIONS_FILE_PATH = "test_signed_transaction.json"
FROM_SELECT_KEY = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
TO_PUBLIC_KEY = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"
time = datetime(2023, 12, 23, 11, 23, 45, 67)


@pytest.fixture
def setup_transaction():
    t = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    blockChain = BlockChain()
    blockChain.append(t)
    blockChain.save(TRANSACTIONS_FILE_PATH)

    yield

    os.remove(TRANSACTIONS_FILE_PATH)


def test_transaction_json():
    transaction = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 12)
    sat = transaction.model_dump_json()
    expect = '{"time":"2023-12-23T11:23:45.000067","sender":"5a43cd741ce01c9241e1071662cc85740d2331c80d2a2d6b32742b677496cad8fa69f64a54e3c61240d1a98ee3fd1be7ad02dd423156d448f9f7efa356a43369","receiver":"b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd","amount":12,"signature":"'
    assert expect in sat


def test_restore_transactions():
    t1 = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    t2 = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 10)
    blockChain1 = BlockChain()
    blockChain1.append(t1)
    blockChain1.append(t2)
    blockChain1.save(TRANSACTIONS_FILE_PATH)

    blockChain2 = BlockChain()
    blockChain2.load(TRANSACTIONS_FILE_PATH)
    transactions = blockChain2.get_transactions()

    assert t1 == transactions[0]
    assert t2 == transactions[1]

    os.remove(TRANSACTIONS_FILE_PATH)


def test_normal_transaction(setup_transaction):
    sat = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    from_pub_key = VerifyingKey.from_string(
        binascii.unhexlify(sat.sender), curve=SECP256k1
    )
    signature = binascii.unhexlify(sat.signature)
    unsigned_json = sat.to_unsigned().model_dump_json()

    from_pub_key.verify(signature, unsigned_json.encode("utf-8"))

    assert True is True


def test_falsification_transaction(setup_transaction):
    # create falsificated transaction from correct transaction by change amount
    # test to fail verify falsificated transaction
    corr = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    fals = Transaction(
        corr.time,
        corr.sender,
        corr.receiver,
        30,
        corr.signature,
    )
    # get public key. both correct and falsificate public keys are same
    from_pub_key = VerifyingKey.from_string(
        binascii.unhexlify(fals.sender), curve=SECP256k1
    )

    fals_signature = binascii.unhexlify(fals.signature)
    fals_unsigned = fals.to_unsigned().model_dump_json()

    # falsicate signature and data(unsigned transaction) cannot verify by from_pub_key.
    with pytest.raises(BadSignatureError) as e:
        from_pub_key.verify(fals_signature, json.dumps(fals_unsigned).encode("utf-8"))

    assert str(e.value) == "Signature verification failed"


# def test_send_same_transaction(setup_transaction):
#     blockChain = BlockChain()
#     blockChain.load(TRANSACTIONS_FILE_PATH)
#     transactions = blockChain.get_transactions()
#     transaction = transactions[0]
#     sat = Transaction(
#         transaction.time,
#         transaction.sender,
#         transaction.receiver,
#         30,
#         transaction.signature,
#     )
#     from_pub_key = VerifyingKey.from_string(
#         binascii.unhexlify(sat.sender), curve=SECP256k1
#     )
#     signature = binascii.unhexlify(sat.signature)
#     unsigned = sat.to_unsigned().model_dump_json()

#     with pytest.raises(BadSignatureError) as e:
#         from_pub_key.verify(signature, json.dumps(unsigned).encode("utf-8"))

#     assert str(e.value) == "Signature verification failed"
