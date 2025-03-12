FROM python:3.12.9-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH=/google-cloud-sdk/bin:$PATH


RUN apt-get update --fix-missing && apt-get install -y git build-essential gcc bzip2 curl ca-certificates && \
    pip install "poetry==2.1.1" && \
    python -m venv /venv

COPY ../poetry.lock python/poetry.lock
COPY ../pyproject.toml python/pyproject.toml
COPY ../README.md python/README.md

COPY ../pixaris python/pixaris
RUN cd python && poetry build && /venv/bin/pip install dist/*.whl

FROM base as final

COPY --from=builder /venv /venv

WORKDIR /home/app

RUN apt-get update --fix-missing && apt-get clean

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH="/venv/bin:$PATH"


ENTRYPOINT []
