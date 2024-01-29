import os
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from blockchain.domain.blockchain import Blockchain, Block
from blockchain.infrastructure.chain_repository_impl import ChainRepositoryImpl

from blockchain.domain.transaction import Transaction
from blockchain.infrastructure.syncer_impl import SyncerImpl
from blockchain.infrastructure.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from blockchain.usecase.usecase import Usecase
from blockchain.settings import Settings, settings


def get_my_adress(settings: Settings) -> str:
    # todo tmp impl
    port = str(settings.port)
    return f"127.0.0.1:{port}"


print("settings:", settings)
cached_dir = ".cache/" + str(settings.port)
if not os.path.exists(cached_dir):
    os.makedirs(cached_dir)

my_adress = get_my_adress(settings)

transaction_repo = TransactionRepositoryImpl(f"{cached_dir}/transactions.json")
transactions = transaction_repo.load_transactios()

chain_repo = ChainRepositoryImpl(f"{cached_dir}/chain.json")
chain = chain_repo.load_chain()

blockchain = Blockchain(outblock_transactions=transactions, chain=chain)

syncer = SyncerImpl()

usecase = Usecase(blockchain, transaction_repo, chain_repo, syncer)

app = FastAPI()


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


@app.post("/transaction/bloadcast")
def post_bloadcast_transaction(transaction: Transaction):
    message = usecase.add_transaction_without_bloadcast(transaction=transaction)
    return {"message": message}


@app.get("/chain")
def get_chain():
    chain = usecase.get_chain()
    return chain


@app.post("/chain")
def post_chain(chain: list[Block]):
    message = usecase.update_chain(chain=chain)
    return {"message": message}
