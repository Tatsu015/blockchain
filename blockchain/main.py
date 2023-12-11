import datetime
from ecdsa import SigningKey, SECP256k1, BadDigestError
from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction:
    time: datetime
    sender: str
    receiver: str
    amount: int


t1 = Transaction(datetime.datetime.now(), "A", "B", 1)
t2 = Transaction(datetime.datetime.now(), "C", "D", 3)
transactions = [t1, t2]
print(transactions)

secret_key = SigningKey.generate(curve=SECP256k1)
print("secret key", secret_key.to_string().hex())
public_key = secret_key.verifying_key
print("public key", public_key.to_string().hex())

doc = "very important data"
signature = secret_key.sign(doc.encode("utf-8"))
print("signature", signature.hex())

# doc = "aaa"
try:
    public_key.verify(signature, doc.encode("utf-8"))
    print("not falsificated")
except BadDigestError:
    print("falsificated")
