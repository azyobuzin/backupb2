# base: Install Python
FROM python:3.7-buster AS base
RUN apt-get update && \
    apt-get install -y --no-install-recommends sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# builder: poetry build
FROM base AS builder
SHELL ["/bin/bash", "-c"]
ENV POETRY_VERSION=1.1.5 POETRY_ACCEPT=1
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python3
COPY pyproject.toml /src/
WORKDIR /src
RUN source $HOME/.poetry/env && poetry install --no-dev
COPY . /src
RUN source $HOME/.poetry/env && poetry build -n -f wheel

# output: Install the built package
FROM base
COPY --from=builder /src/dist /dist
RUN pip3 install --no-cache-dir /dist/*.whl b2 && rm -rf /dist
ENV PYTHONDONTWRITEBYTECODE=1
