#!/usr/bin/env python3
"""
Test creating and using BAF agents with minimal configuration
"""

import asyncio
import json
import os
import sys
import pathlib
import pytest
from pathlib import Path

# Add parent directory to path so we can use relative imports
parent_dir = str(pathlib.Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from baf_client import BAFClient, ModelType, AgentType, OutputFormat

async def test_create_and_use_agent():
    """Test creating a simple agent and using it with different output formats"""
    try:
        print("Creating BAF Agent wrapper...")
        # Use .. to reference parent directory
        credentials_path = os.path.join("..", "agent-binding.json")
        baf = BAFClient(credentials_path, "Minimal Test Agent")
        
        print("Authenticating...")
        await baf._get_token()
        
        print("Creating agent...")
        agent = await baf.create_agent(
            initial_instructions="You are a helpful assistant.",
            expert_in="Answering questions concisely",
            # Using strings directly instead of enums
            agent_type="smart",
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O
        )
        
        print("Agent created successfully!")
        
        # Test with default markdown output
        print("\nTesting with markdown output...")
        md_response = await agent("What is Python? Keep it brief.")
        print(f"Markdown response: {md_response}")
        
        # Test with text output
        print("\nTesting with text output...")
        text_response = await agent("What is Python? Keep it brief.", 
                                   output_format="Text")
        print(f"Text response: {text_response}")
        
        # Test with JSON output
        print("\nTesting with JSON output...")
        json_response = await agent("Name 3 programming languages.", 
                                  output_format="JSON")
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
    asyncio.run(test_create_and_use_agent()) 