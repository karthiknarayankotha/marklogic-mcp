# Use a Python image with uv pre-installed for fast dependency management
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the source URL for the image (optional, for provenance)
LABEL org.opencontainers.image.source="https://github.com/karthiknarayankotha/marklogic-mcp"

# Set the working directory
WORKDIR /app

# Copy the project into the image
ADD . /app


# Install dependencies using uv and install the project in editable mode
#RUN uv sync && uv pip install -e .

RUN pip install --upgrade pip uv
RUN uv pip install --system -e .


WORKDIR /app/src/mcp_marklogic


# Expose the default port (as per README and code, default is 8000)
EXPOSE 8021

# Set environment variables for MarkLogic connection (can be overridden at runtime)
ENV MARKLOGIC_HOST=localhost
ENV MARKLOGIC_PORT=8000
ENV MARKLOGIC_USERNAME=admin
ENV MARKLOGIC_PASSWORD=admin

# Run the MCP MarkLogic server using the project script entrypoint
#CMD ["uv", "--directory", "marklogic_mcp", "run", "server.py"]

CMD ["python", "-m", "mcp_marklogic.main"]