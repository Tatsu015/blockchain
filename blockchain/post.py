import requests


from main import new_transaction


from_secret_key = "9a77f929737b0b2e90090afc57685d734735052deab172aa5228aa65ee0fcbd2"
to_public_key = "b2ec566cff3702724e86ef6fa0d36835d6d5153ff402bca6dc976b7dc308f4bebeda361ae3267d0c3818ca001478f8ac8eb07908ed2e2c4b76cbcfd49720d4dd"
t = new_transaction(from_secret_key, to_public_key, 10)

data = t.to_dict()
res = requests.post("http://127.0.0.1:8080/transaction_pool", json=data)
