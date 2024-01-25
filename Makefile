PHONY:dev
dev:
	export PORT=8080 && poetry run uvicorn blockchain.main:app --port $$PORT

PHONY:dev_reload
dev_reload:
	export PORT=8080 && poetry run uvicorn blockchain.main:app --reload --port $$PORT

PHONY:dev_multi
dev_multi:
	(export PORT=8081 && poetry run uvicorn blockchain.main:app --port $$PORT) & (export PORT=8082 && poetry run uvicorn blockchain.main:app --port $$PORT) & (export PORT=8083 && poetry run uvicorn blockchain.main:app --port $$PORT)

PHONY:dev_8081
dev_8081:
	export PORT=8081 && poetry run uvicorn blockchain.main:app --port $$PORT

PHONY:dev_8082
dev_8082:
	export PORT=8082 && poetry run uvicorn blockchain.main:app --port $$PORT

PHONY:dev_8083
dev_8083:
	export PORT=8083 && poetry run uvicorn blockchain.main:app --port $$PORT

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
