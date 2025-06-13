# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the source URL for the image
LABEL org.opencontainers.image.source="https://github.com/intruder-io/intruder-mcp"

# Copy the project into the image
ADD . /app
# Set environment variables for MarkLogic connection (can be overridden at runtime)
ENV MARKLOGIC_HOST=localhost
ENV MARKLOGIC_PORT=8000
ENV MARKLOGIC_USERNAME=admin
ENV MARKLOGIC_PASSWORD=admin

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync && uv pip install -e .

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "--directory", "mcp_marklogic", "run", "server.py"]