from fastapi.encoders import jsonable_encoder
import requests
from blockchain.domain.syncer import Syncer
from blockchain.domain.transaction import Transaction
from concurrent.futures import ThreadPoolExecutor
from blockchain.settings import settings


class SyncerImpl(Syncer):
    def bloadcast(self, transaction: Transaction):
        hosts = list(filter(None, settings.hosts.split(",")))
        with ThreadPoolExecutor() as exector:
            for host in hosts:
                if host == settings.my_adress():
                    continue
                url = "http://" + host + "/transaction/bloadcast"
                json = jsonable_encoder(transaction)
                exector.submit(requests.post, url, None, json)
