FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
	curl \
	&& rm -rf /var/lib/apt/lists/*

# install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -

# add poetry to path
ENV PATH="${PATH}:/etc/poetry/bin"

# install dependencies
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
	&& poetry install --no-root

COPY . .

ENTRYPOINT ["ankigengpt"]
