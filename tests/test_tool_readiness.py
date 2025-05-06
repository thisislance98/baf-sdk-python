import pytest
import asyncio
import os
import json
import uuid
from pathlib import Path
from baf_client import BAFClient, ModelType, AgentType, OutputFormat

async def test_tool_readiness():
    """Test that tools properly wait for ready state before continuing."""
    
    print("Starting tool readiness test...")
    
    # Get the path to the credentials file in the parent directory
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    credentials_path = parent_dir / "agent-binding.json"
    
    # Initialize BAF agent
    baf = BAFClient(str(credentials_path), name="Tool Readiness Test Agent")
    
    try:
        # Create the agent
        print("Creating agent...")
        agent = await baf.create_agent(
            initial_instructions="You are a helpful assistant that knows about documents.",
            expert_in="Reading documents and answering questions about them",
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O,
        )
        
        # Add a document tool explicitly to test waiting
        print("Adding document tool...")
        tool_id = await baf.add_tool(
            name="document",
            tool_type="document"
        )
        print(f"Document tool created with ID: {tool_id}")
        
        # Now add a document to test resource waiting
        print("Adding test document...")
        document_content = """
        # Test Document
        
        This is a test document to verify that tool and resource waiting is working properly.
        
        ## Key Points
        1. Tools should wait until ready before returning
        2. Resources should wait until ready before returning
        3. The system should properly handle state transitions
        """
        
        doc_id = await agent.add_document(
            doc_name="test_document.md",
            content=document_content,
            content_type="text/markdown"
        )
        print(f"Document added with ID: {doc_id}")
        
        # Test if we can list documents - should show our added document
        print("Listing documents...")
        documents = await agent.list_documents()
        print(f"Found {len(documents)} documents:")
        for doc in documents:
            print(f"- {doc.get('name', 'Unnamed')} (ID: {doc.get('ID', 'Unknown')})")
        
        # Test the agent with a query about the document
        print("\nTesting agent with a query about the document...")
        response = await agent("What is this document about?")
        print(f"\nAgent response:\n{response}")
        
        # Use the AgentInterface method to get document content
        print("\nRetrieving document content...")
        try:
            content = await agent.get_document_content("test_document.md")
            if content:
                print(f"Successfully retrieved document content ({len(content)} characters)")
                print(f"Content sample: {content[:50]}...")
            else:
                print("Failed to retrieve document content")
        except Exception as e:
            print(f"Error retrieving document content: {str(e)}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_tool_readiness()) 