import pytest
import pandas as pd
from ecdsa import SECP256k1, BadSignatureError, VerifyingKey
import binascii
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict

from blockchain.transaction import Transaction, new_transaction
from blockchain.transaction_repository import TransactionRepository

from pydantic import BaseModel, Field
from datetime import datetime

TRANSACTIONS_FILE_PATH = "test_signed_transaction.json"
FROM_SELECT_KEY = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
TO_PUBLIC_KEY = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"
time = datetime(2023, 12, 23, 11, 23, 45, 67)


@pytest.fixture
def setup_transaction():
    t = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 1)
    repo = TransactionRepository(path=TRANSACTIONS_FILE_PATH)
    repo.add(t)
    repo.save()

    yield

    os.remove(TRANSACTIONS_FILE_PATH)


def test_transaction_json():
    transaction = new_transaction(time, FROM_SELECT_KEY, TO_PUBLIC_KEY, 12)
    sat = transaction.model_dump_json()
    expect = '{"time":"2023-12-23T11:23:45.000067","sender":"5a43cd741ce01c9241e1071662cc85740d2331c80d2a2d6b32742b677496cad8fa69f64a54e3c61240d1a98ee3fd1be7ad02dd423156d448f9f7efa356a43369","receiver":"b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd","amount":12,"signature":"'
    assert expect in sat


def test_normal_transaction(setup_transaction):
    repo = TransactionRepository(path=TRANSACTIONS_FILE_PATH)
    transactions = repo.load()
    sat = transactions[0]
    from_pub_key = VerifyingKey.from_string(
        binascii.unhexlify(sat.sender), curve=SECP256k1
    )
    signature = binascii.unhexlify(sat.signature)
    unsigned_json = sat.to_unsigned().model_dump_json()

    from_pub_key.verify(signature, unsigned_json.encode("utf-8"))

    assert True is True


def test_falsification_transaction(setup_transaction):
    repo = TransactionRepository(path=TRANSACTIONS_FILE_PATH)
    transactions = repo.load()
    transaction = transactions[0]
    sat = Transaction(
        transaction.time,
        transaction.sender,
        transaction.receiver,
        30,
        transaction.signature,
    )
    from_pub_key = VerifyingKey.from_string(
        binascii.unhexlify(sat.sender), curve=SECP256k1
    )
    signature = binascii.unhexlify(sat.signature)
    unsigned = sat.to_unsigned().model_dump_json()

    with pytest.raises(BadSignatureError) as e:
        from_pub_key.verify(signature, json.dumps(unsigned).encode("utf-8"))

    assert str(e.value) == "Signature verification failed"
