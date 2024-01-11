from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from blockchain.blockchain import BlockChain, Block

from blockchain.transaction import Transaction


app = FastAPI()

block_chain = BlockChain()
block_chain.load_transactios("transactions.json")
block_chain.load_chain("chain.json")


@app.exception_handler(RequestValidationError)
async def handler(request: Request, e: RequestValidationError):
    print(e)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/transaction_pool")
def get_transaction_pool():
    return block_chain.transactions_pool


@app.post("/transaction_pool")
def post_transaction_pool(transaction: Transaction):
    try:
        transaction.verify()
    except Exception as e:
        return {"message": e.value}

    block_chain.append(transaction)
    block_chain.save_transactions("transactions.json")
    return {"message": "Transaction is posted"}


@app.get("/chain")
def get_chain():
    return block_chain.chain


@app.post("/chain")
def post_chain(chain: list[Block]):
    if len(chain) <= len(block_chain.chain):
        return {"message": "Received chain is ignored"}
    try:
        block_chain.verify(chain)
        block_chain.replace(chain)
        block_chain.save_chain("chain.json")
        block_chain.save_transactions("transactions.json")
        return {"message": "chain is posted"}

    except Exception as e:
        print(e)
        return {"message": str(e)}
