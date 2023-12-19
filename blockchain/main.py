from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from blockchain.transaction import Transaction


app = FastAPI()

transaction_pool = {"transaction": []}


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


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
