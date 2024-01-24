PHONY:dev
dev:
	export PORT=8081 && poetry run uvicorn blockchain.main:app --reload --port $$PORT

PHONY:dev_multi
dev_multi:
	(export PORT=8081 && poetry run uvicorn blockchain.main:app --reload --port $$PORT) & (export PORT=8082 && poetry run uvicorn blockchain.main:app --reload --port $$PORT) & (export PORT=8083 && poetry run uvicorn blockchain.main:app --reload --port $$PORT)

PHONY:dev_8001
dev_8001:
	export PORT=8081 && poetry run uvicorn blockchain.main:app --reload --port $$PORT

PHONY:dev_8002
dev_8002:
	export PORT=8082 && poetry run uvicorn blockchain.main:app --reload --port $$PORT

PHONY:dev_8003
dev_8003:
	export PORT=8083 && poetry run uvicorn blockchain.main:app --reload --port $$PORT

PHONY:clean
clean:
	rm -rf .cache

PHONY:test
test:
	poetry run pytest

PHONY:post
post:
	poetry run python tools/post.py

PHONY:transaction
transaction:
	curl http://127.0.0.1:8080/transaction | jq

PHONY:mining
mining:
	poetry run python tools/mining.py

PHONY:show_accounts
show_accounts:
	poetry run python tools/show_accounts.py

PHONY:keygen
keygen:
	poetry run python tools/keygen.py
