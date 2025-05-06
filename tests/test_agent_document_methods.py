#!/usr/bin/env python3
"""
Test using document management methods directly on agent interface
"""

import pytest
import asyncio
import os
import json
from pathlib import Path

# Import from parent directory
from baf_client import BAFClient, ModelType, AgentType, OutputFormat

async def test_agent_document_methods():
    """Test using the document management methods directly on the agent interface"""
    try:
        print("Starting document methods test...")
        
        # Get the path to the credentials file in the parent directory
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        credentials_path = parent_dir / "agent-binding.json"
        
        print(f"Creating BAF Agent wrapper with credentials from {credentials_path}...")
        baf = BAFClient(str(credentials_path), "Document Methods Test")
        
        print("Creating agent...")
        agent = await baf.create_agent(
            initial_instructions="You are a helpful assistant that provides information about documents.",
            expert_in="Accessing and summarizing document information",
            agent_type=AgentType.SMART,
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O
        )
        
        print("Agent created successfully!")
        
        # Test adding a document directly via the agent interface
        print("\nAdding document directly via agent interface...")
        doc_content = """
        # Neural Networks Overview
        
        Neural networks are computational models inspired by the human brain's structure and function. 
        They consist of multiple layers of interconnected nodes or "neurons" that process and transform data.
        
        ## Key Components
        
        1. **Input Layer**: Receives the initial data
        2. **Hidden Layers**: Process the data through weighted connections
        3. **Output Layer**: Produces the final result
        4. **Activation Functions**: Non-linear functions that determine the output of neurons
        5. **Weights and Biases**: Parameters that are adjusted during training
        
        ## Common Types
        
        - Feedforward Neural Networks (FNN)
        - Convolutional Neural Networks (CNN)
        - Recurrent Neural Networks (RNN)
        - Long Short-Term Memory Networks (LSTM)
        - Generative Adversarial Networks (GAN)
        
        ## Applications
        
        Neural networks are used in many fields including:
        - Image and speech recognition
        - Natural language processing
        - Medical diagnosis
        - Financial forecasting
        - Autonomous vehicles
        """
        
        doc_id = await agent.add_document(
            doc_name="Neural Networks 101",
            content=doc_content
        )
        print(f"Document added with ID: {doc_id}")
        
        # Test with document query
        print("\nTesting query about the document...")
        response1 = await agent("What are the key components of neural networks according to the document?")
        print(f"Response: {response1}")
        
        # List all documents
        print("\nListing all documents...")
        documents = await agent.list_documents()
        print(f"Found {len(documents)} documents:")
        for doc in documents:
            print(f"- {doc.get('name')} (ID: {doc.get('ID')}, State: {doc.get('state')})")
        
        # Try getting document content with error handling
        print("\nGetting document content...")
        try:
            content = await agent.get_document_content("Neural Networks 101")
            if content:
                print(f"Document content (first 100 chars): {content[:100]}...")
            else:
                print("Unable to retrieve document content.")
        except Exception as e:
            print(f"Error retrieving document content: {e}")
        
        # Add another document
        print("\nAdding another document...")
        doc2_content = """
        # Deep Learning vs Machine Learning
        
        While machine learning is a subset of artificial intelligence, deep learning is a subset of machine learning.
        
        ## Key Differences
        
        1. **Data Dependencies**: Deep learning requires larger amounts of data
        2. **Hardware Requirements**: Deep learning typically needs more computational resources
        3. **Feature Engineering**: Machine learning often requires manual feature extraction, while deep learning performs automatic feature extraction
        4. **Problem Solving Approach**: Machine learning breaks problems into parts, deep learning solves end-to-end
        5. **Execution Time**: Deep learning typically takes longer to train
        
        ## When to Use Each
        
        - **Use Machine Learning when**: You have smaller datasets, need explainability, or have limited computational resources
        - **Use Deep Learning when**: You have large datasets, complex problems like image recognition, or don't need to understand the "why" behind predictions
        """
        
        doc2_id = await agent.add_document(
            doc_name="Deep Learning vs ML",
            content=doc2_content
        )
        print(f"Second document added with ID: {doc2_id}")
        
        # Test with a query about both documents
        print("\nTesting query about both documents...")
        response2 = await agent("Compare neural networks and deep learning based on the documents.")
        print(f"Response: {response2}")
        
        # Remove the first document
        print("\nRemoving the first document...")
        removed = await agent.remove_document("Neural Networks 101")
        print(f"Document removed: {removed}")
        
        # Verify document was removed
        print("\nVerifying document was removed...")
        remaining_docs = await agent.list_documents()
        print(f"Remaining documents: {len(remaining_docs)}")
        for doc in remaining_docs:
            print(f"- {doc.get('name')} (ID: {doc.get('ID')})")
        
        # Test what happens when querying about removed document
        print("\nQuerying about removed document...")
        response3 = await agent("What are the key components of neural networks?")
        print(f"Response about removed document: {response3}")
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_agent_document_methods()) 