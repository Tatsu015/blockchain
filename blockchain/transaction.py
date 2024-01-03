from datetime import datetime
from ecdsa import SigningKey, SECP256k1, VerifyingKey
import binascii
from pydantic import BaseModel


class NonPositiveAmountTransactionError(Exception):
    pass


class UnsignedTransaction(BaseModel):
    time: datetime
    sender: str
    receiver: str
    amount: int


class Transaction(BaseModel):
    time: datetime
    sender: str
    receiver: str
    amount: int
    signature: str

    def to_unsigned(self) -> UnsignedTransaction:
        return UnsignedTransaction(
            time=self.time,
            sender=self.sender,
            receiver=self.receiver,
            amount=self.amount,
        )

    def verify(self):
        if self.amount <= 0:
            raise NonPositiveAmountTransactionError(
                f"less than 0 amount not allowed:{self.amount}"
            )

        from_pub_key = VerifyingKey.from_string(
            binascii.unhexlify(self.sender), curve=SECP256k1
        )

        signature = binascii.unhexlify(self.signature)
        unsigned_json = self.to_unsigned().model_dump_json().encode("utf-8")
        from_pub_key.verify(signature, unsigned_json)


def new_transaction(
    time: datetime, from_secret_key: str, to_public_key: str, amount: int
) -> Transaction:
    from_sec_key = SigningKey.from_string(
        binascii.unhexlify(from_secret_key), curve=SECP256k1
    )
    from_pub_key = from_sec_key.verifying_key.to_string().hex()
    unsigned = UnsignedTransaction(
        time=time, sender=from_pub_key, receiver=to_public_key, amount=amount
    )

    s = from_sec_key.sign(unsigned.model_dump_json().encode("utf-8")).hex()
    t = Transaction(
        time=unsigned.time,
        sender=unsigned.sender,
        receiver=unsigned.receiver,
        amount=unsigned.amount,
        signature=s,
    )
    return t
