PHONY:dev
dev:
	poetry run uvicorn blockchain.main:app --reload --port 8080

PHONY:test
test:
	poetry run pytest

PHONY:dev_post
dev_post:
	poetry run python post.py

PHONY:dev_get
dev_get:
	curl http://127.0.0.1:8080/transaction_pool | jq