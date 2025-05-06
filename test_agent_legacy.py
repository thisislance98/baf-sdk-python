#!/usr/bin/env python3
"""
Test creating and using PAB agents with legacy parameter names
"""

import asyncio
from pab_client import PABClient

async def test_create_and_use_agent_legacy():
    """Test creating an agent using legacy parameter names from sizer_example.py"""
    try:
        print("Creating PAB Client wrapper...")
        pab = PABClient("Legacy Test Agent")
        
        print("Creating agent with legacy parameter 'instruction'...")
        agent = await pab.create_agent(initial_instructions="You are a character named Bob")
        print("Agent created successfully!")
        
        # Test with a simple question
        print("\nSending test message...")
        response = await agent("What is your name?")
        print(f"Response: {response}")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_create_and_use_agent_legacy()) 