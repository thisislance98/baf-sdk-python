#!/usr/bin/env python
"""
Test credentials caching functionality in BAFClient
"""

import asyncio
import os
from pathlib import Path
from baf_client import BAFClient, ModelType, AgentType, OutputFormat

async def test_creds_caching():
    """Test the credentials caching functionality in BAFClient"""
    print("Testing credentials caching in BAFClient...")
    
    # Get the path to the credentials file
    current_dir = Path.cwd()
    credentials_path = current_dir / "agent-binding.json"
    
    if not credentials_path.exists():
        print(f"Credentials file not found at: {credentials_path}")
        print("Please provide the correct path to your credentials file:")
        credentials_path = input("> ")
        if not Path(credentials_path).exists():
            print(f"File not found: {credentials_path}")
            return
    
    print("\n1. First initialization with explicit credentials path:")
    baf1 = BAFClient(str(credentials_path), "Caching Test Client 1")
    
    print("\n2. Second initialization with no credentials path (should use cached):")
    baf2 = BAFClient(name="Caching Test Client 2")
    
    print("\n3. Testing that both clients can authenticate:")
    try:
        print("Authenticating client 1...")
        await baf1._get_token()
        print("Authentication successful for client 1")
        
        print("Authenticating client 2...")
        await baf2._get_token()
        print("Authentication successful for client 2")
        
        print("\n4. Creating a simple agent with client 2...")
        agent = await baf2.create_agent(
            initial_instructions="You are a helpful assistant.",
            expert_in="Testing credentials caching",
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O
        )
        
        print("\n5. Testing the agent with a simple query:")
        response = await agent("Hello, is my cached credentials working?")
        print(f"Agent response: {response}")
        
        print("\nCredentials caching test completed successfully!")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_creds_caching()) 