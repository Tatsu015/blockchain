import pytest
import pandas as pd
from ecdsa import SigningKey, SECP256k1, BadSignatureError, VerifyingKey
import binascii
import json
import os
from blockchain.main import Transaction, new_transaction

PKL_FILE_PATH = "test_signed_transaction.pkl"


@pytest.fixture
def setup_transaction():
    from_secret_key = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
    to_public_key = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"
    t = new_transaction(from_secret_key, to_public_key, 1)
    pd.to_pickle(t, PKL_FILE_PATH)

    yield

    os.remove(PKL_FILE_PATH)


def test_normal_transaction(setup_transaction):
    sat: Transaction = pd.read_pickle(PKL_FILE_PATH)
    from_pub_key = VerifyingKey.from_string(
        binascii.unhexlify(sat.sender), curve=SECP256k1
    )
    signature = binascii.unhexlify(sat.signature)
    unsigned = sat.to_unsigned().to_dict()

    from_pub_key.verify(signature, json.dumps(unsigned).encode("utf-8"))

    assert True is True


def test_falsification_transaction(setup_transaction):
    transaction: Transaction = pd.read_pickle(PKL_FILE_PATH)
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
    unsigned = sat.to_unsigned().to_dict()

    with pytest.raises(BadSignatureError) as e:
        from_pub_key.verify(signature, json.dumps(unsigned).encode("utf-8"))

    assert str(e.value) == "Signature verification failed"