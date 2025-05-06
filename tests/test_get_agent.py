#!/usr/bin/env python3
"""
Test getting an existing agent by ID
"""

import pytest
import asyncio
import os
import json
from pathlib import Path

# Import from parent directory
from baf_client import BAFClient, ModelType, AgentType, OutputFormat

# You should replace this with an actual agent ID from a previous run
# or remove it to create a new agent each time
AGENT_ID = None  # Example: "12345678-1234-1234-1234-123456789012"

async def test_get_existing_agent():
    """Test getting an existing agent by ID"""
    try:
        print("Starting get agent test...")
        
        # Get the path to the credentials file in the parent directory
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        credentials_path = parent_dir / "agent-binding.json"
        
        print("Creating BAF Agent wrapper...")
        
        baf = BAFClient(str(credentials_path), "Get Agent Test")
        
        print("Authenticating...")
        await baf._get_token()
        
        # First create an agent if we don't have an ID
        if AGENT_ID is None:
            print("\nNo agent ID provided, creating a new agent first...")
            agent = await baf.create_agent(
                initial_instructions="You are a helpful assistant.",
                expert_in="Answering questions concisely",
                agent_type=AgentType.SMART,
                base_model=ModelType.OPENAI_GPT4O_MINI,
                advanced_model=ModelType.OPENAI_GPT4O
            )
            
            # Get a response from the new agent to verify it works
            response = await agent("Hello, who are you?")
            print(f"New agent response: {response}")
            
            # Store the agent ID from the BAFClient instance
            agent_id = baf._agent_id
            print(f"\nCreated agent with ID: {agent_id}")
            print("You can use this ID in future tests by updating AGENT_ID in the test file.")
        else:
            print(f"\nGetting existing agent with ID: {AGENT_ID}")
            agent_id = AGENT_ID
        
        # Now test getting the agent by ID
        print("\nTesting get_agent method...")
        
        # Create a new BAF wrapper to simulate a new session
        new_baf = BAFClient("agent-binding.json", "Get Agent Test (New Session)")
        
        # Get the existing agent
        existing_agent = await new_baf.get_agent(agent_id)
        
        # Test the agent
        print("\nTesting existing agent...")
        response = await existing_agent("What is the capital of France?")
        print(f"Existing agent response: {response}")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_get_existing_agent()) 