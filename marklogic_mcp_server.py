from fastmcp import FastMCP
from marklogic import Client
from typing import Dict, Any, Optional, List
import json

# Initialize FastMCP
mcp = FastMCP("MarkLogic Explorer")

# MarkLogic connection configuration
ML_HOST = "localhost"  # Replace with your MarkLogic host
ML_PORT = 8000        # Replace with your MarkLogic port
ML_USER = "admin"     # Replace with your MarkLogic username
ML_PASS = "admin"     # Replace with your MarkLogic password

def get_client() -> Client:
    """Create and return a MarkLogic client instance"""
    return Client(ML_HOST, ML_PORT, ML_USER, ML_PASS)

@mcp.resource("database://collections")
def get_collections() -> str:
    """Get all collections in the database"""
    client = get_client()
    try:
        # Query to get all collections
        collections = client.eval("""
            cts.collections()
        """)
        return json.dumps(list(collections), indent=2)
    except Exception as e:
        return f"Error retrieving collections: {str(e)}"

@mcp.tool()
def create_document(uri: str, content: Dict[Any, Any], collections: Optional[List[str]] = None) -> str:
    """Create a new document in MarkLogic
    
    Args:
        uri: Document URI
        content: Document content as dictionary
        collections: Optional list of collections to add the document to
    """
    client = get_client()
    try:
        # Create document
        if collections:
            client.documents.create(
                uri=uri,
                content=content,
                collections=collections
            )
        else:
            client.documents.create(
                uri=uri,
                content=content
            )
        return f"Document created successfully at URI: {uri}"
    except Exception as e:
        return f"Error creating document: {str(e)}"

@mcp.tool()
def query_documents(query_string: str) -> str:
    """Query documents using MarkLogic search
    
    Args:
        query_string: cts.query string or search criteria
    """
    client = get_client()
    try:
        # Execute search query
        results = client.eval(f"""
            xdmp.toJSON(
                cts.search({query_string}).toArray().map(doc => {{
                    uri: xdmp.nodeUri(doc),
                    content: doc.toObject()
                }})
            )
        """)
        return json.dumps(json.loads(results), indent=2)
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.prompt()
def analyze_collection(collection: str) -> str:
    """Create a prompt template for analyzing collections"""
    return f"""Please analyze this MarkLogic collection:
Collection: {collection}
Available Collections: 
{get_collections()}

What insights can you provide about the documents and their structure?"""

if __name__ == "__main__":
    # Start the MCP server
    mcp.run() 