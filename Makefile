PHONY:dev
dev:
	poetry run uvicorn blockchain.main:app --reload --port 8080

PHONY:clean
clean:
	rm -rf .cache

PHONY:test
test:
	poetry run pytest

PHONY:post
post:
	poetry run python post.py

PHONY:transaction
transaction:
	curl http://127.0.0.1:8080/transaction | jq

PHONY:mining
mining:
	poetry run python mining.py

PHONY:show_accounts
show_accounts:
	poetry run python show_accounts.py

PHONY:keygen
keygen:
	poetry run python keygen.py
