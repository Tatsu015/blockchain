import requests
from datetime import datetime

from blockchain.transaction import new_transaction
from fastapi.encoders import jsonable_encoder

from_secret_key = "3492bbbca3e5efe5e1758058d8bbf2101dcaf2a50f8562b79861fc2f194347ca"
# pub = e3a81cfec35827aad5890f96aa19d441c92c5d5a9ba90486be68a0121201957690c23b4788452be49e313e6ed920e59b4d6165d71b82b2d860e5e9a3e25e2c5f

# secret = 4b9c9d512d0c24fe846e7ff1154368c008c4317e5a40d5f7a7014c5713c65cf7
to_public_key = "495a955e239ad845eb7e6048e46fbdd143dce9d1fb9b16eb9b6415d00cfc7a59a47c6f2198fa52781e840bb195153772a75cc689210b8670f2e236c2f8b4b86a"
t = new_transaction(datetime.now(), from_secret_key, to_public_key, 10)

data = jsonable_encoder(t)
print("post data:", data)
res = requests.post("http://127.0.0.1:8080/transaction_pool", json=data)
