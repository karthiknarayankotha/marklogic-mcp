import json
import logging
from typing import Dict, List, Optional, Union
from marklogic import Client
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("MarkLogic Explorer")

# Initialize MarkLogic connection
# Note: These should be configured via environment variables in production
ML_HOST = "http://localhost"
ML_PORT = 8000
ML_USER = "admin"
ML_PASSWORD = "admin"

def get_client():
    """Get MarkLogic client connection using the official Python Client"""
    return Client(
        f"{ML_HOST}:{ML_PORT}",
        digest=(ML_USER, ML_PASSWORD)
    )

@mcp.resource("collections://main")
def get_collections() -> List[str]:
    """Get all collections in the database"""
    client = get_client()
    try:
        response = client.get("/v1/search", params={"category": "collection"})
        collections = response.json().get("collections", [])
        return collections
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def create_document(uri: str, content, collection: Optional[str] = None) -> str:
    """Create a new document in MarkLogic
    
    Args:
        uri: Document URI
        content: Document content (will be converted to appropriate format)
        collection: Optional collection to add the document to
    """
    client = get_client()
    try:
        # Convert content to string if it's not already
        if isinstance(content, (dict, list)):
            data = json.dumps(content)
        else:
            data = str(content)
            
        headers = {"Content-Type": "application/json"}
        if collection:
            headers["ML-Collection"] = collection
            
        response = client.put(
            f"/v1/documents?uri={uri}",
            data=data,
            headers=headers
        )
        
        if response.status_code == 201:
            return f"Document created successfully at {uri}"
        else:
            return f"Error: Unexpected status code {response.status_code}"
    except Exception as e:
        return f"Error creating document: {str(e)}"

@mcp.tool()
def read_document(uri: str) -> str:
    """Read a document from MarkLogic by URI"""
    client = get_client()
    try:
        response = client.get(f"/v1/documents?uri={uri}")
        if response.status_code == 200:
            content = response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            return json.dumps(content, indent=2) if isinstance(content, dict) else str(content)
        else:
            return f"Error: Document not found or access denied (Status: {response.status_code})"
    except Exception as e:
        return f"Error reading document: {str(e)}"

@mcp.tool()
def update_document(uri: str, content: Union[Dict, str]) -> str:
    """Update an existing document in MarkLogic
    
    Args:
        uri: Document URI
        content: New document content (JSON or string)
    """
    client = get_client()
    try:
        # Convert dict to JSON string if needed
        if isinstance(content, dict):
            content = json.dumps(content)
            
        response = client.put(
            f"/v1/documents?uri={uri}",
            data=content,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [201, 204]:
            return f"Document {uri} updated successfully"
        else:
            return f"Error: Unexpected status code {response.status_code}"
    except Exception as e:
        return f"Error updating document: {str(e)}"

@mcp.tool()
def delete_document(uri: str) -> str:
    """Delete a document from MarkLogic by URI"""
    client = get_client()
    try:
        response = client.delete(f"/v1/documents?uri={uri}")
        if response.status_code == 204:
            return f"Document {uri} deleted successfully"
        else:
            return f"Error: Unexpected status code {response.status_code}"
    except Exception as e:
        return f"Error deleting document: {str(e)}"

@mcp.tool()
def search_documents(query: str, collection: Optional[str] = None) -> str:
    """Search for documents in MarkLogic
    
    Args:
        query: Search query string
        collection: Optional collection to search within
    """
    client = get_client()

    try:
        params = {
            "q": query,
            "pageLength": 100,
            "format": "json"
        }
        if collection:
            params["collection"] = collection

        response = client.get("/v1/search", params=params)

        if not response.content or not response.content.strip():
            return "Error: Empty response from MarkLogic"

        if response.status_code == 200:
            try:
                return json.dumps(response.json(), indent=2)
            except json.JSONDecodeError as jde:
                return f"Error: Invalid JSON in response — {str(jde)}\nRaw: {response.text}"
        else:
            return f"Error: Search failed with status code {response.status_code}, body: {response.text}"
    except Exception as e:
        return f"Error searching documents: {str(e)}"

if __name__ == "__main__":
    logging.info("Starting MarkLogic MCP server on http://localhost:8021")
    mcp.run(host="localhost", port=8021)