from mcp.client.fastmcp import FastMCPClient

def test_marklogic_mcp():
    # Create MCP client connecting to port 6277
    client = FastMCPClient("http://localhost:6277")
    
    # Test document creation
    create_response = client.call(
        "create_document",
        uri="/test/hello.json",
        content={"message": "Hello, MarkLogic!"},
        collections=["test"]
    )
    print("Create response:", create_response)
    
    # Test document reading
    read_response = client.call(
        "read_document",
        uri="/test/hello.json"
    )
    print("Read response:", read_response)
    
    # Test search
    search_response = client.call(
        "search_documents",
        query="Hello",
        page_length=10
    )
    print("Search response:", search_response)
    
    # Test document deletion
    delete_response = client.call(
        "delete_document",
        uri="/test/hello.json"
    )
    print("Delete response:", delete_response)

if __name__ == "__main__":
    test_marklogic_mcp() 