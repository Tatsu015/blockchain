from datetime import datetime, timezone
import json
from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError
import binascii
from dataclasses import dataclass, asdict
from pydantic import BaseModel, field_serializer


@dataclass(frozen=True)
class UnsignedTransaction(BaseModel):
    time: datetime
    sender: str
    receiver: str
    amount: int

    @field_serializer(time)
    def serialize_time(self, time: datetime) -> str:
        return time.isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Transaction(UnsignedTransaction):
    signature: str

    def to_unsigned(self) -> UnsignedTransaction:
        return UnsignedTransaction(self.time, self.sender, self.receiver, self.amount)

    def to_dict(self) -> dict:
        return asdict(self)

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
    time: datetime, from_secret_key: str, to_public_key: str, amount: int
) -> Transaction:
    from_sec_key = SigningKey.from_string(
        binascii.unhexlify(from_secret_key), curve=SECP256k1
    )
    from_pub_key = from_sec_key.verifying_key.to_string().hex()

    now = time.isoformat()
    unsigned = {
        "time": now,
        "sender": from_pub_key,
        "receiver": to_public_key,
        "amount": amount,
    }

    s = from_sec_key.sign(json.dumps(unsigned).encode("utf-8")).hex()
    t = Transaction(now, from_pub_key, to_public_key, amount, s)
    return t
