PHONY:dev
dev:
	poetry run uvicorn blockchain.main:app --reload --port 8080

PHONY:test
test:
	poetry run pytest

PHONY:dev_post
dev_post:
	poetry run python blockchain/post.py
