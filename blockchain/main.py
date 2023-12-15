from datetime import datetime
import pandas as pd
import json
from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError
import binascii
from dataclasses import dataclass, asdict
from pydantic import BaseModel
from fastapi import FastAPI


@dataclass(frozen=True)
class UnsignedTransaction:
    time: datetime
    sender: str
    receiver: str
    amount: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Transaction(BaseModel):
    time: datetime
    sender: str
    receiver: str
    amount: int
    signature: str

    def to_unsigned(self) -> UnsignedTransaction:
        return UnsignedTransaction(self.time, self.sender, self.receiver, self.amount)

    def verify(self) -> bool:
        from_pub_key = VerifyingKey.from_string(
            binascii.unhexlify(self.sender), curve=SECP256k1
        )

        signature = binascii.unhexlify(self.signature)
        unsigned = self.to_unsigned().to_dict()
        try:
            from_pub_key.verify(signature, json.dumps(unsigned).encode("utf-8"))
            return True
        except BadSignatureError as e:
            print(e)
            return False


def new_transaction(
    from_secret_key: str, to_public_key: str, amount: int
) -> Transaction:
    from_sec_key = SigningKey.from_string(
        binascii.unhexlify(from_secret_key), curve=SECP256k1
    )
    from_pub_key = from_sec_key.verifying_key.to_string().hex()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    unsigned = {
        "time": now,
        "sender": from_pub_key,
        "receiver": to_public_key,
        "amount": amount,
    }

    s = from_sec_key.sign(json.dumps(unsigned).encode("utf-8")).hex()
    t = Transaction(now, from_pub_key, to_public_key, amount, s)
    return t


app = FastAPI()

transaction_pool = {"transaction": []}


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/api/transaction_pool")
def get_transaction_pool():
    return transaction_pool


@app.post("/api/transaction_pool")
def post_transaction_pool(transaction: Transaction):
    if transaction.verify():
        transaction_pool["transaction"].append(transaction.model_dump())

    return {"message": "Transaction is posted"}
