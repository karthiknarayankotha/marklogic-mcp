# MarkLogic MCP Server

This project implements a FastMCP server for MarkLogic, providing document creation and querying capabilities.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MarkLogic connection:
Edit the following variables in `marklogic_mcp_server.py`:
```python
ML_HOST = "localhost"  # Your MarkLogic host
ML_PORT = 8000        # Your MarkLogic port
ML_USER = "admin"     # Your MarkLogic username
ML_PASS = "admin"     # Your MarkLogic password
```

3. Run the server:
```bash
python marklogic_mcp_server.py
```

## Features

### 1. Create Documents
Create new documents in MarkLogic with optional collection assignment:
```python
create_document(
    uri="/documents/example.json",
    content={"title": "Example", "content": "Hello World"},
    collections=["my-collection"]
)
```

### 2. Query Documents
Query documents using MarkLogic's cts.query:
```python
query_documents('cts.andQuery([cts.collectionQuery("my-collection")])')
```

### 3. List Collections
Get all collections in the database:
```python
get_collections()
```

### 4. Analyze Collections
Generate insights about collections:
```python
analyze_collection("my-collection")
``` 