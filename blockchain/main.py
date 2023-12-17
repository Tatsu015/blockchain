from fastapi import FastAPI

from blockchain.transaction import Transaction


app = FastAPI()

transaction_pool = {"transaction": []}


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/transaction_pool")
def get_transaction_pool():
    return transaction_pool


@app.post("/transaction_pool")
def post_transaction_pool(transaction: Transaction):
    if transaction.verify():
        transaction_pool["transaction"].append(transaction)

    return {"message": "Transaction is posted"}
