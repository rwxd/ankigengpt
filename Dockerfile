FROM docker.io/python:3.14-alpine@sha256:faee120f7885a06fcc9677922331391fa690d911c020abb9e8025ff3d908e510

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.9 /uv /bin/uv

# Create venv
#RUN uv venv /opt/venv
RUN uv venv /opt/venv

# Use the virtual environment automatically
ENV VIRTUAL_ENV=/opt/venv

# Place entry points in the environment at the front of the path
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY pyproject.toml ./
RUN uv pip install --compile-bytecode -r pyproject.toml

COPY . .

ENTRYPOINT ["ankigengpt"]
