from datetime import datetime
from blockchain.blockchain import (
    Blockchain,
    accounts,
    integrate_inblock_transactions,
    mining,
)
from blockchain.transaction import new_transaction
from blockchain.usecase import Usecase

pub_key_a = "e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f"
sec_key_a = "3492bbbca3e5efe5e1758058d8bbf2101dcaf2a50f8562b79861fc2f194347ca"

pub_key_b = "495a955e239ad845eb7e6048e46fbdd143dce9d1fb9b16eb9b6415d00cfc7a59a47c6f2198fa52781e840bb195153772a75cc689210b8670f2e236c2f8b4b86a"
sec_key_b = "4b9c9d512d0c24fe846e7ff1154368c008c4317e5a40d5f7a7014c5713c65cf7"

pub_key_c = "b8860d19e29a40f0f1aa78903accf58faff869c869ca355e37ef3ded50fdfb3664cef1e80d8672e1eae365c5cad1625b58432b5c19afb6f26656efce5b26ec89"
sec_key_c = "7b3162dd8ca1f49b3fb005fa6868468bccde9baced924d004d04c38a522dc21f"

pub_key_d = "3519798ce1d1cbece8f80183ab3383d3893353338a0e359b513c4aa6ce134f322844c5939f455d4af26a6711aeb593d36472d3a28da2b96e9190c151ae4587f0"
sec_key_d = "880f333800e295a892b7dc7a3a41f70430b8fdc8bc5832728f93ed636ea5cd5b"


def test_usecase1():
    remote_blockchain = Blockchain(outblock_transactions=[], chain=[])

    remote_uc = Usecase(remote_blockchain)

    ###
    # first mining
    ###
    local_blockchain1 = Blockchain(
        outblock_transactions=remote_blockchain.outblock_transactions.copy(),
        chain=remote_blockchain.chain.copy(),
    )
    new_block = mining(
        miner_public_key=pub_key_a,
        outblock_transactions=local_blockchain1.outblock_transactions.copy(),
        chain=local_blockchain1.chain.copy(),
    )
    local_blockchain1.add_block(new_block)
    remote_uc.update_chain(local_blockchain1.chain)

    chain = remote_uc.get_chain()
    transactions = remote_uc.get_outblock_transaction()

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
    remote_uc.add_transaction(
        new_transaction(
            time=datetime.now(),
            from_secret_key=sec_key_a,
            to_public_key=pub_key_b,
            amount=123,
        ),
    )

    chain = remote_uc.get_chain()
    transactions = remote_uc.get_outblock_transaction()

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
    local_blockchain2 = Blockchain(
        outblock_transactions=remote_blockchain.outblock_transactions.copy(),
        chain=remote_blockchain.chain.copy(),
    )
    new_block = mining(
        miner_public_key=pub_key_b,
        outblock_transactions=local_blockchain2.outblock_transactions.copy(),
        chain=local_blockchain2.chain.copy(),
    )

    local_blockchain2.add_block(new_block)
    remote_uc.update_chain(local_blockchain2.chain)

    chain = remote_uc.get_chain()
    transactions = remote_uc.get_outblock_transaction()

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

    acs = accounts(integrate_inblock_transactions(local_blockchain2.chain))
    assert acs[pub_key_a] == 133
    assert acs[pub_key_b] == 379


def test_usecase2():
    remote_blockchain = Blockchain(outblock_transactions=[], chain=[])

    remote_uc = Usecase(remote_blockchain)

    ###
    # A -> C : 5coin false
    ###
    remote_uc.add_transaction(
        new_transaction(
            time=datetime.now(),
            from_secret_key=sec_key_a,
            to_public_key=pub_key_c,
            amount=5,
        ),
    )
    acs = accounts(remote_blockchain.inblock_transactions)
    assert len(acs) == 0

    ###
    # C -> D : 3coin false
    ###
    remote_uc.add_transaction(
        new_transaction(
            time=datetime.now(),
            from_secret_key=sec_key_a,
            to_public_key=pub_key_c,
            amount=3,
        ),
    )
    acs = accounts(remote_blockchain.inblock_transactions)
    assert len(acs) == 0

    ###
    # A mining : get 256coin
    ###
    # local_blockchain = Blockchain()
    # new_block = uc.mining(
    #     blockchain=local_blockchain,
    #     miner_public_key=pub_key_a,
    #     transactions=remote_blockchain.outblock_transactions.copy(),
    #     chain=remote_blockchain.chain.copy(),
    # )
    # local_blockchain.chain.append(new_block)
    # uc.add_chain(remote_blockchain, local_blockchain.chain)

    # local_blockchain.refresh_inblock_transactions()
    # acs = accounts(local_blockchain.inblock_transactions)
    # assert len(acs) == 1
    # assert acs[pub_key_a] == 256

    # ###
    # # C -> B : 10coin false
    # ###
    # uc.add_transaction(
    #     remote_blockchain,
    #     new_transaction(
    #         time=datetime.now(),
    #         from_secret_key=sec_key_c,
    #         to_public_key=pub_key_b,
    #         amount=10,
    #     ),
    # )
    # local_blockchain.refresh_inblock_transactions()
    # acs = accounts(local_blockchain.inblock_transactions)
    # assert len(acs) == 1
    # assert acs[pub_key_a] == 256

    # ###
    # # C mining : get 256coin
    # ###
    # new_block = uc.mining(
    #     blockchain=local_blockchain,
    #     miner_public_key=pub_key_c,
    #     transactions=[],
    #     chain=remote_blockchain.chain.copy(),
    # )
    # local_blockchain.chain.append(new_block)
    # uc.add_chain(remote_blockchain, local_blockchain.chain)

    # local_blockchain.refresh_inblock_transactions()
    # acs = accounts(local_blockchain.inblock_transactions)
    # assert len(acs) == 2
    # assert acs[pub_key_a] == 256
    # assert acs[pub_key_c] == 256

    # ###
    # # C -> D : 10coin false
    # ###
    # uc.add_transaction(
    #     remote_blockchain,
    #     new_transaction(
    #         time=datetime.now(),
    #         from_secret_key=sec_key_c,
    #         to_public_key=pub_key_d,
    #         amount=10,
    #     ),
    # )
    # local_blockchain.refresh_inblock_transactions()
    # acs = accounts(local_blockchain.inblock_transactions)
    # assert len(acs) == 2
    # assert acs[pub_key_a] == 256
    # assert acs[pub_key_c] == 256

    # ###
    # # D mining : get 256coin
    # ###
    # new_block = uc.mining(
    #     blockchain=local_blockchain,
    #     miner_public_key=pub_key_d,
    #     transactions=[],
    #     chain=remote_blockchain.chain.copy(),
    # )
    # local_blockchain.chain.append(new_block)
    # uc.add_chain(remote_blockchain, local_blockchain.chain)

    # local_blockchain.refresh_inblock_transactions()
    # acs = accounts(local_blockchain.inblock_transactions)
    # assert len(acs) == 3
    # assert acs[pub_key_a] == 256
    # assert acs[pub_key_c] == 246
    # assert acs[pub_key_d] == 10

    # chain = uc.get_chain(remote_blockchain)
    # transactions = uc.get_outblock_transaction(remote_blockchain)

    # # assert len(transactions) == 1
    # # assert transactions[0].amount == 123
    # # assert transactions[0].sender == pub_key_a
    # # assert transactions[0].receiver == pub_key_b
    # # assert len(chain) == 2
    # # assert chain[0].transactions == []
    # # assert len(chain[1].transactions) == 1
    # # assert chain[1].transactions[0].amount == 256
    # # assert chain[1].transactions[0].sender == "Blockchain"
    # # assert chain[1].transactions[0].receiver == pub_key_a

    # # ###
    # # # 2nd mining
    # # ###
    # # new_block = uc.mining(
    # #     blockchain=local_blockchain,
    # #     miner_public_key=pub_key_b,
    # #     transactions=remote_blockchain.outblock_transactions,
    # #     chain=remote_blockchain.chain.copy(),
    # # )

    # # local_blockchain.chain.append(new_block)
    # # uc.add_chain(remote_blockchain, local_blockchain.chain)

    # # chain = uc.get_chain(remote_blockchain)
    # # transactions = uc.get_outblock_transaction(remote_blockchain)

    # # assert len(transactions) == 0
    # # assert len(chain) == 3
    # # assert chain[0].transactions == []
    # # assert len(chain[1].transactions) == 1
    # # assert chain[1].transactions[0].amount == 256
    # # assert chain[1].transactions[0].sender == "Blockchain"
    # # assert chain[1].transactions[0].receiver == pub_key_a
    # # assert len(chain[2].transactions) == 2
    # # assert chain[2].transactions[0].amount == 123
    # # assert chain[2].transactions[0].sender == pub_key_a
    # # assert chain[2].transactions[0].receiver == pub_key_b
    # # assert chain[2].transactions[1].amount == 256
    # # assert chain[2].transactions[1].sender == "Blockchain"
    # # assert chain[2].transactions[1].receiver == pub_key_b

    # # local_blockchain.refresh_inblock_transactions()
    # # acs = accounts(local_blockchain.inblock_transactions)
    # # assert acs[pub_key_a] == 133
    # # assert acs[pub_key_b] == 379
