from marklogic import Client
import logging
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from typing import Any, Optional
import json

logger = logging.getLogger('mcp_marklogic')
logger.info("Starting MCP MarkLogic Server")

class MarkLogicDatabase:
    def __init__(self, host: str, port: int, username: str, password: str):
        """Initialize connection to the MarkLogic database"""
        logger.debug(f"Initializing database connection to {host}:{port}")
        self.client = Client(f"http://{host}:{port}", digest=(username, password))

    def create_document(self, uri: str, content: Any, collections: Optional[list[str]] = None) -> dict:
        """Create a document in MarkLogic"""
        try:
            response = self.client.documents.write(uri=uri, content=content, collections=collections)
            logger.debug(f"Created document at {uri}")
            return {"status": "success", "uri": uri}
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise

    def read_document(self, uri: str) -> Any:
        """Read a document from MarkLogic"""
        try:
            response = self.client.get(f"/v1/documents?uri={uri}")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to read document: {response.text}")
        except Exception as e:
            logger.error(f"Error reading document: {e}")
            raise

    def delete_document(self, uri: str) -> dict:
        """Delete a document from MarkLogic"""
        try:
            response = self.client.delete(f"/v1/documents?uri={uri}")
            if response.status_code == 204:
                return {"status": "success", "uri": uri}
            else:
                raise Exception(f"Failed to delete document: {response.text}")
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    def search_documents(self, query: str, collections: Optional[list[str]] = None) -> list[dict]:
        """Search documents in MarkLogic"""
        try:
            params = {"q": query}
            if collections:
                params["collection"] = collections
            response = self.client.get("/v1/search", params=params)
            if response.status_code == 200:
                return response.json()["results"]
            else:
                raise Exception(f"Failed to search documents: {response.text}")
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

async def main(marklogic_host: str, marklogic_port: int, marklogic_username: str, marklogic_password: str):
    logger.info(f"Connecting to MarkLogic MCP Server at {marklogic_host}:{marklogic_port}")

    db = MarkLogicDatabase(marklogic_host, marklogic_port, marklogic_username, marklogic_password)
    server = Server("marklogic-manager")

    # Register handlers
    logger.debug("Registering handlers")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="create-document",
                description="Create a document in MarkLogic",
                annotations={
                    "destructiveHint": True,
                    "idempotentHint": False,
                    "readOnlyHint": False,
                    "title": "Create Document"
                },
                inputSchema={
                    "type": "object",
                    "properties": {
                        "uri": {"type": "string", "description": "URI for the document"},
                        "content": {"type": "object", "description": "Document content"},
                        "collections": {"type": "array", "items": {"type": "string"}, "description": "Collections to add the document to"}
                    },
                    "required": ["uri", "content"],
                },
            ),
            types.Tool(
                name="read-document",
                description="Read a document from MarkLogic",
                annotations={
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "readOnlyHint": True,
                    "title": "Read Document"
                },
                inputSchema={
                    "type": "object",
                    "properties": {
                        "uri": {"type": "string", "description": "URI of the document to read"},
                    },
                    "required": ["uri"],
                },
            ),
            types.Tool(
                name="delete-document",
                description="Delete a document from MarkLogic",
                annotations={
                    "destructiveHint": True,
                    "idempotentHint": True,
                    "readOnlyHint": False,
                    "title": "Delete Document"
                },
                inputSchema={
                    "type": "object",
                    "properties": {
                        "uri": {"type": "string", "description": "URI of the document to delete"},
                    },
                    "required": ["uri"],
                },
            ),
            types.Tool(
                name="search-documents",
                description="Search documents in MarkLogic",
                annotations={
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "readOnlyHint": True,
                    "title": "Search Documents"
                },
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query string"},
                        "collections": {"type": "array", "items": {"type": "string"}, "description": "Collections to search in"}
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "create-document":
                result = db.create_document(
                    uri=arguments["uri"],
                    content=arguments["content"],
                    collections=arguments.get("collections")
                )
                return [types.TextContent(type="text", text=json.dumps(result))]

            elif name == "read-document":
                result = db.read_document(arguments["uri"])
                return [types.TextContent(type="text", text=json.dumps(result))]

            elif name == "delete-document":
                result = db.delete_document(arguments["uri"])
                return [types.TextContent(type="text", text=json.dumps(result))]

            elif name == "search-documents":
                results = db.search_documents(
                    query=arguments["query"],
                    collections=arguments.get("collections")
                )
                return [types.TextContent(type="text", text=json.dumps(results))]
            
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="marklogic",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
