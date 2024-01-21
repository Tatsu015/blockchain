from datetime import datetime
from blockchain.block import Block
from blockchain.blockchain import Blockchain, find_new_block, has_minus_amount
from blockchain.transaction import Transaction


class MiningError(Exception):
    pass


class Usecase:
    def __init__(self, blockchain: Blockchain) -> None:
        self._blockchain = blockchain
        pass

    def get_outblock_transaction(self) -> list[Transaction]:
        return self._blockchain.outblock_transactions

    def add_transaction(self, transaction: Transaction) -> str:
        try:
            transaction.verify()
        except Exception as e:
            return e.value

        self._blockchain.add_transaction(transaction)
        self._blockchain.save_transactions("transactions.json")
        return "Transaction is posted"

    def get_chain(self) -> list[Block]:
        return self._blockchain.chain

    def add_chain(self, chain: list[Block]) -> str:
        if len(chain) <= len(self._blockchain.chain):
            return "Received chain is ignored"
        try:
            self._blockchain.verify(chain)
            self._blockchain.replace(chain)
            self._blockchain.save_chain("chain.json")
            self._blockchain.save_transactions("transactions.json")
            return "chain is posted"

        except Exception as e:
            print(e)
            return str(e)

    def mining(
        self,
        miner_public_key: str,
        outblock_transactions: list[Transaction],
        chain: list[Block],
    ) -> Block:
        if len(chain) < 1:
            raise MiningError("empty chain not allowed")

        copied_outblock_transactions = outblock_transactions.copy()
        self._blockchain.chain = chain
        copied_inblock_transactions = (
            self._blockchain.integrate_inblock_transactions().copy()
        )
        for t in copied_outblock_transactions:
            copied_inblock_transactions.append(t)
            if has_minus_amount(copied_inblock_transactions):
                outblock_transactions.remove(t)
                copied_inblock_transactions.remove(t)

        self._blockchain._outblock_transactions = outblock_transactions

        block = find_new_block(
            now=datetime.now(),
            miner=miner_public_key,
            outblock_transactions=self._blockchain.outblock_transactions,
            chain=self._blockchain.chain,
        )

        return block
