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

docs:
	sphinx-apidoc -o docs .
	cd docs && make html

build-docker-image:
	gcloud builds submit --region=europe-west4 --config docker/cloudbuild.yaml --ignore-file docker/.gcloudignore

deploy-gradio-app-local:
	poetry run gradio pixaris/frontend/main.py

deploy-gradio-app-to-app-engine:
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	@project_id=$$(python -c "import yaml; print(yaml.safe_load(open('pixaris/config.yaml'))['gcp_project_id_for_app_engine'])")
	@service_account=$$(python -c "import yaml; print(yaml.safe_load(open('pixaris/config.yaml'))['gcp_service_account_for_appengine_deployment'])") && \
    gcloud app deploy  app.yaml --project=$$project_id --service-account=$$service_account

