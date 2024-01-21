from datetime import datetime
from blockchain.block import Block
from blockchain.blockchain import Blockchain, find_new_block, has_minus_amount
from blockchain.transaction import Transaction


class MiningError(Exception):
    pass


class Usecase:
    def __init__(self) -> None:
        pass

    def get_outblock_transaction(self, blockchain: Blockchain) -> list[Transaction]:
        return blockchain.outblock_transactions

    def add_transaction(self, blockchain: Blockchain, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        blockchain.add_transaction(transaction)
        blockchain.save_transactions("transactions.json")
        return "Transaction is posted"

    def get_chain(self, blockchain: Blockchain) -> list[Block]:
        return blockchain.chain

    def add_chain(self, blockchain: Blockchain, chain: list[Block]) -> str:
        if len(chain) <= len(blockchain.chain):
            return "Received chain is ignored"
        try:
            blockchain.verify(chain)
            blockchain.replace(chain)
            blockchain.save_chain("chain.json")
            blockchain.save_transactions("transactions.json")
            return "chain is posted"

        except Exception as e:
            print(e)
            return str(e)

    def mining(
        self,
        blockchain: Blockchain,
        miner_public_key: str,
        outblock_transactions: list[Transaction],
        chain: list[Block],
    ) -> Block:
        if len(chain) < 1:
            raise MiningError("empty chain not allowed")

        copied_outblock_transactions = outblock_transactions.copy()
        blockchain.chain = chain
        copied_inblock_transactions = blockchain.integrate_inblock_transactions().copy()
        for t in copied_outblock_transactions:
            copied_inblock_transactions.append(t)
            if has_minus_amount(copied_inblock_transactions):
                outblock_transactions.remove(t)
                copied_inblock_transactions.remove(t)

        blockchain._outblock_transactions = outblock_transactions

        block = find_new_block(
            now=datetime.now(),
            miner=miner_public_key,
            outblock_transactions=blockchain.outblock_transactions,
            chain=blockchain.chain,
        )

        return block
