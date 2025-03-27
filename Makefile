.ONESHELL:
.PHONY: install lint fmt test docs

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

build-docker-image:
	gcloud builds submit --region=europe-west4 --config docker/cloudbuild.yaml --ignore-file docker/.gcloudignore

deploy-gradio-app-local:
	poetry run gradio pixaris/frontend/main.py
