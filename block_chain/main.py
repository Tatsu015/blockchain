import datetime
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
