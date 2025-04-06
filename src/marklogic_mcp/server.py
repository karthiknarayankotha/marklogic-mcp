from mcp.server.fastmcp import FastMCP
from marklogic import Client
import logging
import toml
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import typer

def load_config():
    """Load configuration from pyproject.toml"""
    config_path = Path("pyproject.toml")
    if not config_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    config = toml.load(config_path)
    return config.get("tool", {}).get("marklogic", {})

# Load configuration
config = load_config()

# Configure logging
log_config = config.get("logging", {})
logging.basicConfig(
    level=getattr(logging, log_config.get("level", "INFO")),
    format=log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger("marklogic-mcp")

# Initialize FastMCP server
mcp = FastMCP("marklogic-mcp")

# Initialize MarkLogic client using REST API
client = Client(
    f"http://{config.get('host', 'localhost')}:{config.get('port', 8000)}",
    digest=(config.get('user', 'admin'), config.get('password', 'admin'))
)

@mcp.tool()
async def create_document(uri: str, content: Dict[str, Any], collections: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a new document in MarkLogic"""
    logger.info(f"Creating document at URI: {uri}")
    try:
        if collections is None:
            collections = []
        
        # Convert content to JSON if it's a dict
        if isinstance(content, dict):
            content = json.dumps(content)
            
        params = {}
        if collections:
            params['collection'] = collections
            
        response = client.put(
            f"/v1/documents?uri={uri}",
            params=params,
            data=content,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            return {"status": "success", "message": f"Document created at {uri}"}
        else:
            return {"status": "error", "message": f"Failed to create document: {response.text}"}
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def read_document(uri: str) -> Dict[str, Any]:
    """Read a document from MarkLogic"""
    logger.info(f"Reading document at URI: {uri}")
    try:
        response = client.get(
            f"/v1/documents?uri={uri}",
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "content": response.json() if response.text else None
            }
        else:
            return {"status": "error", "message": f"Failed to read document: {response.text}"}
    except Exception as e:
        logger.error(f"Error reading document: {str(e)}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def update_document(uri: str, content: Dict[str, Any], collections: Optional[List[str]] = None) -> Dict[str, Any]:
    """Update a document in MarkLogic"""
    logger.info(f"Updating document at URI: {uri}")
    try:
        if collections is None:
            collections = []
            
        # Convert content to JSON if it's a dict
        if isinstance(content, dict):
            content = json.dumps(content)
            
        params = {}
        if collections:
            params['collection'] = collections
            
        response = client.put(
            f"/v1/documents?uri={uri}",
            params=params,
            data=content,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [201, 204]:
            return {"status": "success", "message": f"Document updated at {uri}"}
        else:
            return {"status": "error", "message": f"Failed to update document: {response.text}"}
    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def delete_document(uri: str) -> Dict[str, Any]:
    """Delete a document from MarkLogic"""
    logger.info(f"Deleting document at URI: {uri}")
    try:
        response = client.delete(f"/v1/documents?uri={uri}")
        
        if response.status_code in [204, 404]:
            return {"status": "success", "message": f"Document deleted at {uri}"}
        else:
            return {"status": "error", "message": f"Failed to delete document: {response.text}"}
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def search_documents(query: Optional[str] = None, structured_query: Optional[Dict[str, Any]] = None, start: int = 1, page_length: int = 10) -> Dict[str, Any]:
    """Search for documents in MarkLogic using string query or structured query"""
    logger.info(f"Searching documents with query: {query or structured_query}")
    try:
        params = {
            'pageLength': page_length,
            'start': start,
            'format': 'json'
        }
        
        if query:
            params['q'] = query
        elif structured_query:
            params['structuredQuery'] = json.dumps(structured_query)
            
        response = client.get(
            "/v1/search",
            params=params,
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            results = response.json()
            return {
                "status": "success",
                "total": results.get('total', 0),
                "results": results.get('results', []),
                "facets": results.get('facets', {})
            }
        else:
            return {"status": "error", "message": f"Search failed: {response.text}"}
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return {"status": "error", "message": str(e)}

@mcp.resource("schema://main")
async def get_database_info() -> Dict[str, Any]:
    """Get MarkLogic database information as a resource"""
    logger.info("Fetching MarkLogic database information...")
    try:
        response = client.get("/v1/resources/databases")
        
        if response.status_code == 200:
            return {
                "status": "success",
                "databases": response.json()
            }
        else:
            return {"status": "error", "message": f"Failed to fetch database info: {response.text}"}
    except Exception as e:
        logger.error(f"Error fetching database info: {str(e)}")
        return {"status": "error", "message": str(e)}

app = typer.Typer()

@app.command()
def start():
    """Start the MarkLogic MCP server"""
    logger.info("Starting MarkLogic MCP server via CLI...")
    mcp.run(transport="stdio")

def cli():
    """Entry point for the uvx marklogic-mcp command"""
    app()

if __name__ == "__main__":
    # Initialize and run the server
    logger.info("Starting MarkLogic MCP server...")
    mcp.run(transport="stdio") 