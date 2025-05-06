#!/usr/bin/env python3
"""
Test creating and using a smart PAB agent
"""

import pytest
import asyncio
import os
import tempfile
import httpx
import json
import uuid
from pathlib import Path

# Import from parent directory
from pab_client import PABClient, ModelType, AgentType, OutputFormat

async def test_smart_agent():
    """Test creating a smart agent and using it with different output formats"""
    try:
        # Get the path to the credentials file in the parent directory (for display only)
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        credentials_path = parent_dir / "agent-binding.json"
        print(f"Credentials file should be available at: {credentials_path}")
        
        print("Creating first PABClient using cached credentials...")
        # First client with no explicit credentials path - should use cached
        pab1 = PABClient(name="Smart Test Agent 1")
        
        print("Creating second PABClient also using cached credentials...")
        # Second client without credentials path - should use cached
        pab2 = PABClient(name="Smart Test Agent 2")
        
        print("Authenticating...")
        
        print("Creating smart agent...")
        agent = await pab2.create_agent(
            initial_instructions="You are a helpful assistant that provides concise answers.",
            expert_in="Providing factual information"
        )
        
        print("Smart agent created successfully!")
        
        # Test with default markdown output
        print("\nTesting with markdown output...")
        md_response = await agent.send_message(
            "What is the capital of France?",
            output_format=OutputFormat.MARKDOWN
        )
        print(f"Markdown response: {md_response}")
        
        # Test with text output
        print("\nTesting with text output...")
        text_response = await agent.send_message(
            "List three planets in our solar system.", 
            output_format=OutputFormat.TEXT
        )
        print(f"Text response: {text_response}")
        
        # Test with JSON output
        print("\nTesting with JSON output...")
        json_response = await agent.send_message(
            "Give me the population of the 3 most populous countries.", 
            output_format=OutputFormat.JSON
        )
        print(f"JSON response: {json_response}")
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_smart_agent()) 