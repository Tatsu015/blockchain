from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from blockchain.blockchain import FIRST_BLOCK, Blockchain, Block
from blockchain.chain_repository_impl import ChainRepositoryImpl

from blockchain.transaction import Transaction
from blockchain.transaction_repository_impl import TransactionRepositoryImpl
from blockchain.usecase import Usecase


app = FastAPI()

transaction_repo = TransactionRepositoryImpl("transactions.json")
transactions = transaction_repo.load_transactios()

chain_repo = ChainRepositoryImpl("chain.json")
chain = chain_repo.load_chain()

blockchain = Blockchain(outblock_transactions=transactions, chain=chain)

usecase = Usecase(blockchain)


@app.exception_handler(RequestValidationError)
async def handler(_: Request, e: RequestValidationError):
    print(e)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/transaction")
def get_transaction():
    transactions = usecase.get_outblock_transaction()
    return transactions


@app.post("/transaction")
def post_transaction(transaction: Transaction):
    message = usecase.add_transaction(transaction=transaction)
    return {"message": message}


@app.get("/chain")
def get_chain():
    chain = usecase.get_chain()
    return chain


@app.post("/chain")
def post_chain(chain: list[Block]):
    message = usecase.update_chain(chain=chain)
    return {"message": message}
