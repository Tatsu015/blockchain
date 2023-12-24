from datetime import datetime
from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError
import binascii
from dataclasses import dataclass
from pydantic import BaseModel, PrivateAttr


@dataclass(frozen=True)
class UnsignedTransaction(BaseModel):
    time: datetime
    sender: str
    receiver: str
    amount: int


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
        if self.amount <= 0:
            print("less than 0 amount not arrowed")
            return False

        from_pub_key = VerifyingKey.from_string(
            binascii.unhexlify(self.sender), curve=SECP256k1
        )

        signature = binascii.unhexlify(self.signature)
        unsigned_json = self.to_unsigned().model_dump_json().encode("utf-8")
        try:
            from_pub_key.verify(signature, unsigned_json)
            return True
        except BadSignatureError as e:
            print(e)
            return False


def new_transaction(
    time: datetime, from_secret_key: str, to_public_key: str, amount: int
) -> Transaction:
    from_sec_key = SigningKey.from_string(
        binascii.unhexlify(from_secret_key), curve=SECP256k1
    )
    from_pub_key = from_sec_key.verifying_key.to_string().hex()
    unsigned = UnsignedTransaction(time, from_pub_key, to_public_key, amount)

    s = from_sec_key.sign(unsigned.model_dump_json().encode("utf-8")).hex()
    t = Transaction(
        unsigned.time, unsigned.sender, unsigned.receiver, unsigned.amount, s
    )
    return t
