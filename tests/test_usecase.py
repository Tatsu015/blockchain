from datetime import datetime
from blockchain.blockchain import Blockchain, accounts
from blockchain.transaction import new_transaction
from blockchain.usecase import Usecase

pub_key_a = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"
sec_key_a = "3492bbbca3e5efe5e1758058d8bbf2101dcaf2a50f8562b79861fc2f194347ca"

pub_key_b = "495a955e239ad845eb7e6048e46fbdd143dce9d1fb9b16eb9b6415d00cfc7a59a47c6f2198fa52781e840bb195153772a75cc689210b8670f2e236c2f8b4b86a"
sec_key_b = "4b9c9d512d0c24fe846e7ff1154368c008c4317e5a40d5f7a7014c5713c65cf7"


def test_usecase():
    remote_blockchain = Blockchain()
    local_blockchain = Blockchain()

    print("local", id(local_blockchain.chain))
    print("remot", id(remote_blockchain.chain))

    uc = Usecase()

    ###
    # first mining
    ###
    new_block = uc.mining(
        blockchain=local_blockchain,
        miner_public_key=pub_key_a,
        transactions=[],
        chain=remote_blockchain.chain.copy(),  # use default chain
    )
    local_blockchain.chain.append(new_block)
    uc.add_chain(remote_blockchain, local_blockchain.chain)

    chain = uc.get_chain(remote_blockchain)
    transactions = uc.get_outblock_transaction(remote_blockchain)

    # initial chain and first create chain exist
    assert transactions == []
    assert len(chain) == 2
    assert chain[0].transactions == []
    assert len(chain[1].transactions) == 1
    assert chain[1].transactions[0].amount == 256
    assert chain[1].transactions[0].sender == "Blockchain"
    assert chain[1].transactions[0].receiver == pub_key_a

    ###
    # 1st transaction create
    ###
    uc.add_transaction(
        remote_blockchain,
        new_transaction(
            time=datetime.now(),
            from_secret_key=sec_key_a,
            to_public_key=pub_key_b,
            amount=123,
        ),
    )

    chain = uc.get_chain(remote_blockchain)
    transactions = uc.get_outblock_transaction(remote_blockchain)

    assert len(transactions) == 1
    assert transactions[0].amount == 123
    assert transactions[0].sender == pub_key_a
    assert transactions[0].receiver == pub_key_b
    assert len(chain) == 2
    assert chain[0].transactions == []
    assert len(chain[1].transactions) == 1
    assert chain[1].transactions[0].amount == 256
    assert chain[1].transactions[0].sender == "Blockchain"
    assert chain[1].transactions[0].receiver == pub_key_a

    ###
    # 2nd mining
    ###
    new_block = uc.mining(
        blockchain=local_blockchain,
        miner_public_key=pub_key_b,
        transactions=remote_blockchain.outblock_transactions,
        chain=remote_blockchain.chain.copy(),
    )

    local_blockchain.chain.append(new_block)
    uc.add_chain(remote_blockchain, local_blockchain.chain)

    chain = uc.get_chain(remote_blockchain)
    transactions = uc.get_outblock_transaction(remote_blockchain)

    assert len(transactions) == 0
    assert len(chain) == 3
    assert chain[0].transactions == []
    assert len(chain[1].transactions) == 1
    assert chain[1].transactions[0].amount == 256
    assert chain[1].transactions[0].sender == "Blockchain"
    assert chain[1].transactions[0].receiver == pub_key_a
    assert len(chain[2].transactions) == 2
    assert chain[2].transactions[0].amount == 123
    assert chain[2].transactions[0].sender == pub_key_a
    assert chain[2].transactions[0].receiver == pub_key_b
    assert chain[2].transactions[1].amount == 256
    assert chain[2].transactions[1].sender == "Blockchain"
    assert chain[2].transactions[1].receiver == pub_key_b

    local_blockchain.refresh_inblock_transactions()
    acs = accounts(local_blockchain.inblock_transactions)
    assert acs[pub_key_a] == 133
    assert acs[pub_key_b] == 379
