# MCP MarkLogic Server

This is a Model Context Protocol (MCP) server implementation for MarkLogic, allowing you to interact with a MarkLogic database through MCP tools.

2. The server provides the following operations:

### Create Document

- Create documents in MarkLogic with optional collections
- Read documents by URI
- Delete documents by URI
- Search documents with query strings and optional collection filters

## Installation

```bash
pip install mcp-marklogic
```

## Configuration

The server requires the following environment variables:

```bash
MARKLOGIC_HOST=localhost
MARKLOGIC_PORT=8000
MARKLOGIC_USERNAME=admin
MARKLOGIC_PASSWORD=admin
```

## Usage

Once installed and configured, you can start the server:

```bash
mcp-marklogic
```

### Available Tools

1. `create-document`

   - Create a new document in MarkLogic
   - Parameters:
     - `uri`: Document URI (required)
     - `content`: Document content as JSON (required)
     - `collections`: List of collections to add the document to (optional)

2. `read-document`

   - Read a document from MarkLogic
   - Parameters:
     - `uri`: Document URI (required)

3. `delete-document`

   - Delete a document from MarkLogic
   - Parameters:
     - `uri`: Document URI (required)

4. `search-documents`
   - Search for documents in MarkLogic
   - Parameters:
     - `query`: Search query string (required)
     - `collections`: List of collections to search in (optional)

## Development

### Setup

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies:
   ```bash
   pip install -e .
   ```

### Running Tests

```bash
pytest tests/
```

### MarkLogic Setup

1. Ensure you have MarkLogic Server installed and running
2. Create a REST API instance on port 8000 if not already present
3. Create a user with appropriate permissions:
   - Go to Admin Interface (usually http://localhost:8001)
   - Create role `python-docs-role` with:
     - Roles: `rest-extension-user`, `rest-reader`, `rest-writer`
     - Privileges: `xdbc:eval`, `xdbc:invoke`, `xdmp:eval-in`
   - Create user `python-user` with:
     - Password: `pyth0n`
     - Role: `python-docs-role`

## License

MIT
