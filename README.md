# MarkLogic MCP Server

A Python-based MCP (Model-Controller-Processor) server for MarkLogic database operations. This server provides CRUD operations and search functionality for MarkLogic documents through a standardized interface using the MarkLogic REST API.

## Features

- Document CRUD operations (Create, Read, Update, Delete)
- Document search with string and structured queries
- Collection management
- Database information retrieval
- TOML-based configuration
- Comprehensive logging
- Full REST API support

## Prerequisites

- Python 3.7+
- MarkLogic Server (installed and running)
- Access to a MarkLogic database with appropriate permissions
- REST API instance configured on MarkLogic server

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/marklogic-mcp.git
cd marklogic-mcp
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your server:

```bash
cp pyproject.toml.example pyproject.toml
```

Edit the `pyproject.toml` file with your MarkLogic connection details:

```toml
[tool.marklogic]
host = "localhost"
port = 8000
user = "your-username"
password = "your-password"

[tool.marklogic.logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Usage

1. Start the MCP server:

```bash
python marklogic_mcp_server.py
```

2. The server provides the following operations:

### Create Document

```python
create_document(uri: str, content: dict, collections: list = None)
```

### Read Document

```python
read_document(uri: str)
```

### Update Document

```python
update_document(uri: str, content: dict, collections: list = None)
```

### Delete Document

```python
delete_document(uri: str)
```

### Search Documents

```python
search_documents(
    query: str = None,           # String query (e.g., "marklogic and python")
    structured_query: dict = None,  # Structured query in JSON format
    start: int = 1,             # Starting position
    page_length: int = 10       # Number of results per page
)
```

### Get Database Information

```python
get_database_info()
```

## Example Usage

```python
# Create a document
response = create_document(
    uri="/documents/example.json",
    content={"title": "Example", "content": "This is a test"},
    collections=["test-collection"]
)

# Search using string query
response = search_documents(
    query="marklogic and python",
    start=1,
    page_length=10
)

# Search using structured query
response = search_documents(
    structured_query={
        "query": {
            "term-query": {
                "text": ["marklogic"]
            }
        }
    },
    start=1,
    page_length=10
)
```

## Configuration

The server is configured using `pyproject.toml`. Here are the available configuration options:

```toml
[tool.marklogic]
host = "localhost"      # MarkLogic server host
port = 8000            # MarkLogic server port
user = "admin"         # MarkLogic username
password = "admin"     # MarkLogic password

[tool.marklogic.logging]
level = "INFO"         # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Log format
```

## Response Format

All operations return a dictionary with a `status` field indicating success or failure:

```python
# Success response
{
    "status": "success",
    "message": "Operation result message",
    "content": "Document content (for read operations)",
    "total": "Total results (for search operations)",
    "results": "Search results array",
    "facets": "Search facets (if available)"
}

# Error response
{
    "status": "error",
    "message": "Error message"
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
