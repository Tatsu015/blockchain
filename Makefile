PHONY:dev
dev:
	poetry run python blockchain/main.py

PHONY:test
test:
	poetry run pytest
