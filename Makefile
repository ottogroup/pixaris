.ONESHELL:
.PHONY: install install-all lint fmt test docs

install:
	poetry install

install-all:
	poetry install --with gcp,cluster,dev
	$(MAKE) install

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
	find _build/html/ -name "*.html" -exec sed -i '/<head>/a\  <meta name="google-site-verification" content="h26qQkhbY1Ju2W-Y83o7aFaM9jCft9ztjL5sBMJmNAE" />' {} +

deploy-gradio-app-to-app-engine:
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	@project_id=$$(python -c "import yaml; print(yaml.safe_load(open('config.yaml'))['gcp_project_id_for_app_engine'])")
	@service_account=$$(python -c "import yaml; print(yaml.safe_load(open('config.yaml'))['gcp_service_account_for_appengine_deployment'])") && \
    gcloud app deploy  app.yaml --project=$$project_id --service-account=$$service_account

