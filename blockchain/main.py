from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from blockchain.blockchain import BlockChain

from blockchain.transaction import Transaction


app = FastAPI()


block_chain = BlockChain()
block_chain.load("transactions.json")


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/transaction_pool")
def get_transaction_pool():
    return block_chain.get_transactions()


@app.post("/transaction_pool")
def post_transaction_pool(transaction: Transaction):
    try:
        transaction.verify()
    except Exception as e:
        return {"message": e.value}

    block_chain.append(transaction)
    return {"message": "Transaction is posted"}
