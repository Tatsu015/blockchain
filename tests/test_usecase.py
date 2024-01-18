from blockchain.blockchain import Blockchain
from blockchain.usecase import Usecase

miner_a = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"


def test_usecase():
    blockchain = Blockchain()
    sut = Usecase()

    sut.mining(
        blockchain=blockchain,
        miner_public_key=miner_a,
        transactions=[],
        chain=blockchain.chain,  # use default chain
    )

    assert sut.get_outblock_transaction(blockchain) == []
    chain = sut.get_chain(blockchain)
    assert len(chain) == 2
    assert chain[0].transactions == []
    reward_transaction = chain[1].transactions[0]
    assert reward_transaction.amount == 256
    assert reward_transaction.sender == "Blockchain"
