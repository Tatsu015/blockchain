import datetime
import pandas as pd
import json
from ecdsa import SigningKey, SECP256k1, BadSignatureError
import binascii
from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction:
    time: datetime
    sender: str
    receiver: str
    amount: int
    signature: str

def new_transaction(from_secret_key:str, to_public_key:str, amount:int)->Transaction:
    from_sec_key = SigningKey.from_string(binascii.unhexlify(from_secret_key), curve=SECP256k1)
    from_pub_key = from_sec_key.verifying_key.to_string().hex()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    unsigned = {"time":now, "sender":from_pub_key, "receiver":to_public_key, "amount":amount}
   
    s = from_sec_key.sign(json.dumps(unsigned).encode('utf-8')).hex()

    t = Transaction(now, from_sec_key,to_public_key, amount, s)
    return t

from_secret_key = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
to_public_key = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"
t = new_transaction(from_secret_key, to_public_key, 1)

pd.to_pickle(t, "signed_transaction.pkl")
