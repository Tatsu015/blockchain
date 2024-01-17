from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from blockchain.blockchain import BlockChain, Block

from blockchain.transaction import Transaction
from blockchain.usecase import Usecase


app = FastAPI()

blockchain = BlockChain()
blockchain.load_transactios("transactions.json")
blockchain.load_chain("chain.json")
usecase = Usecase(blockchain=blockchain)


@app.exception_handler(RequestValidationError)
async def handler(_: Request, e: RequestValidationError):
    print(e)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/transaction_pool")
def get_transaction_pool():
    transactions = usecase.get_transaction_pool()
    return transactions


@app.post("/transaction_pool")
def post_transaction_pool(transaction: Transaction):
    message = usecase.add_transaction_pool(transaction)
    return {"message": message}


@app.get("/chain")
def get_chain():
    chain = usecase.get_chain()
    return chain


@app.post("/chain")
def post_chain(chain: list[Block]):
    message = usecase.add_chain(chain)
    return {"message": message}
