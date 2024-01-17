from blockchain.block import Block
from blockchain.blockchain import BlockChain
from blockchain.transaction import Transaction


class Usecase:
    def __init__(self, blockchain: BlockChain) -> None:
        self.__blockchain = blockchain

    def get_transaction_pool(self) -> list[Transaction]:
        return self.__blockchain.transactions_pool

    def add_transaction_pool(self, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        self.__blockchain.append(transaction)
        self.__blockchain.save_transactions("transactions.json")
        return "Transaction is posted"

    def get_chain(self) -> list[Block]:
        return self.__blockchain.chain

    def add_chain(self, chain: list[Block]) -> str:
        if len(chain) <= len(self.__blockchain.chain):
            return "Received chain is ignored"
        try:
            self.__blockchain.verify(chain)
            self.__blockchain.replace(chain)
            self.__blockchain.save_chain("chain.json")
            self.__blockchain.save_transactions("transactions.json")
            return "chain is posted"

        except Exception as e:
            print(e)
            return str(e)
