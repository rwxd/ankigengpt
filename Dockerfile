FROM docker.io/python:3.13-alpine@sha256:bb1f2fdb1065c85468775c9d680dcd344f6442a2d1181ef7916b60a623f11d40

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.9@sha256:ba36ea627a75e2a879b7f36efe01db5a24038f8d577bd7214a6c99d5d4f4b20c /uv /bin/uv

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
