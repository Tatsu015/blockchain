import os
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from blockchain.domain.blockchain import Blockchain, Block
from blockchain.infrastructure.chain_repository_impl import ChainRepositoryImpl

from blockchain.domain.transaction import Transaction
from blockchain.infrastructure.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from blockchain.usecase.usecase import Usecase
from blockchain.settings import settings

print("settings:", settings)
cached_dir = ".cache/" + settings.cache_dir
if not os.path.exists(dir):
    os.makedirs(cached_dir)

app = FastAPI()

transaction_repo = TransactionRepositoryImpl(f"{cached_dir}/transactions.json")
transactions = transaction_repo.load_transactios()

chain_repo = ChainRepositoryImpl(f"{cached_dir}/chain.json")
chain = chain_repo.load_chain()

blockchain = Blockchain(outblock_transactions=transactions, chain=chain)

usecase = Usecase(blockchain, transaction_repo, chain_repo)


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
