.ONESHELL:
.PHONY: install lint fmt

install:
	poetry install

lint:
	set -e
	poetry run ruff format --check
	poetry run ruff check

fmt:
	poetry run ruff format
	poetry run ruff check --fix

test:
	poetry run pytest
