import os
import pytest
from mcp_marklogic.server import MarkLogicDatabase

@pytest.fixture(scope="function")
def marklogic():
    """Create a MarkLogic client using environment variables for connection details."""
    host = os.environ.get("MARKLOGIC_HOST", "localhost")
    port = int(os.environ.get("MARKLOGIC_PORT", "8000"))
    username = os.environ.get("MARKLOGIC_USERNAME", "python-user")
    password = os.environ.get("MARKLOGIC_PASSWORD", "pyth0n")
    
    db = MarkLogicDatabase(host, port, username, password)
    
    # Clean up any test documents that might exist
    try:
        db.delete_document("/test/doc1.json")
        db.delete_document("/test/doc2.json")
        db.delete_document("/test/doc3.json")
    except:
        pass
        
    yield db

@pytest.mark.asyncio
async def test_create_document(marklogic):
    # Create a test document
    doc = {
        "name": "Test Document",
        "value": 123
    }
    result = marklogic.create_document(
        uri="/test/doc1.json",
        content=doc,
        collections=["test-collection"]
    )
    
    # Verify the document creation
    assert result["status"] == "success"
    assert result["uri"] == "/test/doc1.json"

    # Read back the document to verify content
    read_doc = marklogic.read_document("/test/doc1.json")
    assert read_doc["name"] == "Test Document"
    assert read_doc["value"] == 123

@pytest.mark.asyncio
async def test_read_document(marklogic):
    # Create a test document first
    doc = {
        "name": "Another Test",
        "value": 456
    }
    marklogic.create_document("/test/doc2.json", doc)
    
    # Read the document
    result = marklogic.read_document("/test/doc2.json")
    
    # Verify the document content
    assert result["name"] == "Another Test"
    assert result["value"] == 456

@pytest.mark.asyncio
async def test_delete_document(marklogic):
    # Create a test document first
    doc = {
        "name": "To Be Deleted",
        "value": 789
    }
    marklogic.create_document("/test/doc3.json", doc)
    
    # Delete the document
    result = marklogic.delete_document("/test/doc3.json")
    
    # Verify deletion
    assert result["status"] == "success"
    assert result["uri"] == "/test/doc3.json"
    
    # Try to read the deleted document - should raise an exception
    with pytest.raises(Exception) as exc_info:
        marklogic.read_document("/test/doc3.json")
    assert "Failed to read document" in str(exc_info.value)

@pytest.mark.asyncio
async def test_search_documents(marklogic):
    # Create test documents
    docs = [
        {
            "uri": "/test/doc1.json",
            "content": {"name": "First Document", "type": "test"},
            "collections": ["test-collection"]
        },
        {
            "uri": "/test/doc2.json",
            "content": {"name": "Second Document", "type": "test"},
            "collections": ["test-collection"]
        }
    ]
    
    for doc in docs:
        marklogic.create_document(doc["uri"], doc["content"], doc["collections"])
    
    # Search for documents
    results = marklogic.search_documents(
        query="Document",
        collections=["test-collection"]
    )
    
    # Verify search results
    assert len(results) == 2
    assert any(doc["uri"] == "/test/doc1.json" for doc in results)
    assert any(doc["uri"] == "/test/doc2.json" for doc in results)

    # Search with more specific query
    results = marklogic.search_documents(
        query="First Document",
        collections=["test-collection"]
    )
    
    # Verify filtered results
    assert len(results) == 1
    assert results[0]["uri"] == "/test/doc1.json" 