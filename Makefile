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

create-docker-image-podman:
	podman build -t pixaris_image . -f docker/Dockerfile

docs:
	sphinx-apidoc -o docs .
	cd docs && make html
	
build-docker-image:
	gcloud builds submit --region=europe-west4 --config docker/cloudbuild.yaml --ignore-file docker/.gcloudignore
