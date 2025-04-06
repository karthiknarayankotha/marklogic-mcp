import os
import pytest
import asyncio
import json
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
from mcp_marklogic.server import MarkLogicDatabase

class MockStream:
    def __init__(self):
        self.messages = []
        self.closed = False

    async def send(self, message):
        self.messages.append(message)

    async def receive(self):
        return self.messages.pop(0) if self.messages else None

    async def close(self):
        self.closed = True

@pytest.fixture
def marklogic():
    host = os.environ.get("MARKLOGIC_HOST", "localhost")
    port = int(os.environ.get("MARKLOGIC_PORT", "8000"))
    username = os.environ.get("MARKLOGIC_USERNAME", "python-user")
    password = os.environ.get("MARKLOGIC_PASSWORD", "pyth0n")
    
    db = MarkLogicDatabase(host, port, username, password)
    
    # Clean up any test documents
    try:
        db.delete_document("/test/server-doc1.json")
        db.delete_document("/test/server-doc2.json")
    except:
        pass
        
    return db

@pytest.fixture
def server(marklogic):
    server = Server("marklogic-test")
    
    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [
            Tool(
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
                        "uri": {"type": "string"},
                        "content": {"type": "object"},
                        "collections": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["uri", "content"],
                },
            ),
            Tool(
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
                        "uri": {"type": "string"},
                    },
                    "required": ["uri"],
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "create-document":
            result = marklogic.create_document(
                uri=arguments["uri"],
                content=arguments["content"],
                collections=arguments.get("collections")
            )
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "read-document":
            result = marklogic.read_document(arguments["uri"])
            return [TextContent(type="text", text=json.dumps(result))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")

    return server

@pytest.mark.asyncio
async def test_server_initialization():
    """Test that the server initializes correctly"""
    read_stream = MockStream()
    write_stream = MockStream()
    
    server = Server("marklogic-test")
    
    # Start server initialization
    init_task = asyncio.create_task(
        server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="marklogic",
                server_version="0.1.0",
                capabilities=server.get_capabilities(),
            ),
        )
    )
    
    # Wait a bit for initialization
    await asyncio.sleep(0.1)
    
    # Check initialization message was sent
    assert len(write_stream.messages) > 0
    init_message = json.loads(write_stream.messages[0])
    assert init_message["type"] == "initialize"
    assert init_message["serverInfo"]["name"] == "marklogic"
    assert init_message["serverInfo"]["version"] == "0.1.0"
    
    # Clean up
    init_task.cancel()
    try:
        await init_task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_server_tool_list(server):
    """Test that the server returns the correct list of tools"""
    read_stream = MockStream()
    write_stream = MockStream()
    
    # Start server
    server_task = asyncio.create_task(
        server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="marklogic",
                server_version="0.1.0",
                capabilities=server.get_capabilities(),
            ),
        )
    )
    
    # Wait for initialization
    await asyncio.sleep(0.1)
    
    # Send list tools request
    read_stream.messages.append(json.dumps({
        "type": "request",
        "id": "test-1",
        "method": "listTools",
        "params": {}
    }))
    
    # Wait for response
    await asyncio.sleep(0.1)
    
    # Check response
    response = json.loads(write_stream.messages[-1])
    assert response["type"] == "response"
    assert response["id"] == "test-1"
    assert len(response["result"]) == 2
    assert response["result"][0]["name"] == "create-document"
    assert response["result"][1]["name"] == "read-document"
    
    # Clean up
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_server_create_document(server, marklogic):
    """Test creating a document through the server"""
    read_stream = MockStream()
    write_stream = MockStream()
    
    # Start server
    server_task = asyncio.create_task(
        server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="marklogic",
                server_version="0.1.0",
                capabilities=server.get_capabilities(),
            ),
        )
    )
    
    # Wait for initialization
    await asyncio.sleep(0.1)
    
    # Send create document request
    read_stream.messages.append(json.dumps({
        "type": "request",
        "id": "test-2",
        "method": "callTool",
        "params": {
            "name": "create-document",
            "arguments": {
                "uri": "/test/server-doc1.json",
                "content": {"name": "Server Test", "value": 123},
                "collections": ["test-collection"]
            }
        }
    }))
    
    # Wait for response
    await asyncio.sleep(0.1)
    
    # Check response
    response = json.loads(write_stream.messages[-1])
    assert response["type"] == "response"
    assert response["id"] == "test-2"
    result = json.loads(response["result"][0]["text"])
    assert result["status"] == "success"
    assert result["uri"] == "/test/server-doc1.json"
    
    # Verify document was created
    doc = marklogic.read_document("/test/server-doc1.json")
    assert doc["name"] == "Server Test"
    assert doc["value"] == 123
    
    # Clean up
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass 